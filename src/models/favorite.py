"""Favorite SQLAlchemy Model definition."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base
from .types import GUID


class Favorite(Base):
    """Favorite Table Definition."""

    __tablename__ = "favorites"
    __allow_unmapped__ = True
    __table_args__ = (UniqueConstraint("user_id", "request_id", name="uq_favorite_user_request"),)

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False)
    request_id = Column(
        GUID(),
        ForeignKey("requests.id", ondelete="CASCADE"),  # NOTE: Not enforced by DSQL; handled by SQLAlchemy cascade
        nullable=False,
    )  # TODO: Enhance this behaviour, to keep maybe only title available so that users are not
    # surprised when the request owner deletes the request. For now it just vanishes

    created_at: "datetime" = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # default lazy mode kept, as sometimes we want to check only if the favorite exist.
    # We dont want to load complete request object with it
    request = relationship("Request", back_populates="favorites", lazy="select")

    # TODO: not sure if we should return requests here, or should we let the client do a GET for
    # how many requests there are might be too much (even though favorites number is limited)
    def to_dict(self) -> dict[str, str]:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "request_id": str(self.request_id),
            "created_at": self.created_at.isoformat(),
        }
