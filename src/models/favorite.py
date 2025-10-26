# src/models/favorite.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .types import GUID
from .request import Base


class Favorite(Base):
    __tablename__ = "favorites"
    __allow_unmapped__ = True
    __table_args__ = (
        UniqueConstraint("user_id", "request_id", name="uq_favorite_user_request"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False)
    request_id = Column(
        GUID(),
        ForeignKey("requests.id", ondelete="CASCADE"),
        nullable=False,
    )  # TODO: Enhance this behaviour, to keep maybe only title available so that users are not surprised when the request owner deletes the request. For now it just vanishes

    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False,
    )

    request = relationship(
        "Request", lazy="select"
    )  # default lazy mode kept, as sometimes we want to check only if the favorite exist. We dont want to load complete request object with it

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "request_id": str(self.request_id),
            "created_at": self.created_at.isoformat(),
        }
