import uuid
from sqlalchemy.types import TypeDecorator, CHAR


class GUID(TypeDecorator):
    """Platform-independent UUID type.

    Uses PostgreSQL native UUID, otherwise stores as CHAR(36).
    This is to allow quick & easy testing with SQLLite
    Returns Python uuid.UUID objects.
    """

    impl = CHAR

    # FIXME: Add this to fix performance issue/warning from sqlalchemy
    # cache_ok = True
    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import UUID

            return dialect.type_descriptor(UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(str(value))
        if dialect.name == "postgresql":
            return value
        else:
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(value)
