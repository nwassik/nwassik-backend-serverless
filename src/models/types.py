"""SQL Types Definitions."""

import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import CHAR, TypeDecorator


class GUID(TypeDecorator):
    """Platform-independent UUID type.

    Uses PostgreSQL native UUID, otherwise stores as CHAR(36).
    This is to allow quick & easy testing with SQLLite
    Returns Python uuid.UUID objects.
    """

    impl = CHAR

    # FIXME: Add this to fix performance issue/warning from sqlalchemy (cache_ok = True)
    def load_dialect_impl(self, dialect):  # noqa
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):  # noqa
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(str(value))
        if dialect.name == "postgresql":
            return value
        return str(value)

    def process_result_value(self, value, dialect):  # noqa
        if value is None:
            return value
        return uuid.UUID(value)
