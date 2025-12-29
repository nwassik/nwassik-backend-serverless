"""Session Manager For Application DB."""

import os
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker

from src.config import DATABASE_URL


def _generate_dsql_token(client, hostname, region, db_role):
    """Generate IAM token for Aurora DSQL connection.

    AWS provides two separate API methods:
    - generate_db_connect_admin_auth_token: for predefined admin role
    - generate_db_connect_auth_token: for custom database roles (role specified in connection URL)

    Both methods have the same signature: (Hostname, Region, ExpiresIn)
    The database role is NOT passed to token generation - it's in the connection URL username.
    """
    if db_role == "admin":
        return client.generate_db_connect_admin_auth_token(hostname, region)
    else:
        # For custom roles like app_user, use generate_db_connect_auth_token
        # The role name is specified in the connection URL (username), not here
        return client.generate_db_connect_auth_token(hostname, region)


# For Aurora DSQL, we need to refresh IAM tokens on each connection
if "auroradsql" in DATABASE_URL:
    import boto3

    # Parse the connection URL once
    _url = make_url(DATABASE_URL)
    _hostname = _url.host
    _region = os.environ["AWS_REGION"]
    _db_role = _url.username  # Extract role from DATABASE_URL (admin or app_user)
    _dsql_client = boto3.client("dsql", region_name=_region)

    # Generate initial token
    _initial_token = _generate_dsql_token(_dsql_client, _hostname, _region, _db_role)
    _auth_url = _url.set(password=_initial_token)

    engine = create_engine(
        _auth_url,
        connect_args={"sslmode": "require"},
        pool_pre_ping=True,
        pool_recycle=600,  # Recycle connections after 10 minutes (tokens expire in 15)
    )

    # Refresh token on each checkout from pool
    @event.listens_for(engine, "do_connect")
    def receive_do_connect(dialect, conn_rec, cargs, cparams):
        """Generate fresh IAM token for each new connection."""
        token = _generate_dsql_token(_dsql_client, _hostname, _region, _db_role)
        cparams["password"] = token

else:
    # Non-DSQL databases (SQLite for local dev)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


# NOTE: Aurora DSQL handles connection pooling automatically (no proxy needed)
# IAM auth tokens auto-refresh via the do_connect event listener above
# In case I go back to RDS, I need to use RDS proxy for connections pooling
@contextmanager
def get_db_session():  # noqa
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
