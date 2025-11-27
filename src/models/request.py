"""Favorite SQLAlchemy Model definition."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
)
from sqlalchemy.orm import relationship

from src.schemas.request import RequestType

from .base import Base
from .types import GUID


# TODO: Add fragile field, item size and weight
class Request(Base):
    """Request base Table Definition."""

    __tablename__ = "requests"
    __allow_unmapped__ = True  # This is to keep my annotations for type hints for now

    # default value is Python side generated and not DB Side
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False)

    type: "RequestType" = Column(Enum(RequestType), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)

    due_date: "datetime" = Column(DateTime(timezone=True), nullable=True)
    created_at: "datetime" = Column(DateTime(timezone=True), default=datetime.now)

    # Relationships for easy access
    buy_and_deliver: "BuyAndDeliverRequest" = relationship(
        "BuyAndDeliverRequest",
        uselist=False,
        cascade="all, delete",
        lazy="joined",  # ⬅️ Always eager load with JOIN
    )
    pickup_and_deliver: "PickupAndDeliverRequest" = relationship(
        "PickupAndDeliverRequest",
        uselist=False,
        cascade="all, delete",
        lazy="joined",
    )
    online_service: "OnlineServiceRequest" = relationship(
        "OnlineServiceRequest",
        uselist=False,
        cascade="all, delete",
        lazy="joined",
    )

    def to_dict(self) -> dict[str, str]:
        tmp_due_date = None
        if self.due_date:
            tmp_due_date = self.due_date.isoformat()
        data = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "type": self.type.value,
            "title": self.title,
            "description": self.description,
            "due_date": tmp_due_date,
            "created_at": self.created_at.isoformat(),
        }

        if self.buy_and_deliver:
            data.update(self.buy_and_deliver.to_dict())
        elif self.pickup_and_deliver:
            data.update(self.pickup_and_deliver.to_dict())
        elif self.online_service:
            data.update(self.online_service.to_dict())

        return data


class BuyAndDeliverRequest(Base):
    """BuyAndDeliverRequest Table Definition."""

    __tablename__ = "buy_and_deliver_requests"

    request_id = Column(
        GUID(),
        ForeignKey("requests.id", ondelete="CASCADE"),
        primary_key=True,
    )
    dropoff_latitude = Column(Float, nullable=False)
    dropoff_longitude = Column(Float, nullable=False)

    request = relationship("Request", back_populates="buy_and_deliver")

    def to_dict(self) -> dict[str, Float]:
        # Only return subtype-specific fields
        return {
            "dropoff_latitude": self.dropoff_latitude,
            "dropoff_longitude": self.dropoff_longitude,
        }


class PickupAndDeliverRequest(Base):
    """PickupAndDeliverRequest Table Definition."""

    __tablename__ = "pickup_and_deliver_requests"

    request_id = Column(
        GUID(),
        ForeignKey("requests.id", ondelete="CASCADE"),
        primary_key=True,
    )
    pickup_latitude = Column(Float, nullable=False)
    pickup_longitude = Column(Float, nullable=False)
    dropoff_latitude = Column(Float, nullable=False)
    dropoff_longitude = Column(Float, nullable=False)

    request = relationship("Request", back_populates="pickup_and_deliver")

    def to_dict(self) -> dict[str, Float]:
        return {
            "pickup_latitude": self.pickup_latitude,
            "pickup_longitude": self.pickup_longitude,
            "dropoff_latitude": self.dropoff_latitude,
            "dropoff_longitude": self.dropoff_longitude,
        }


class OnlineServiceRequest(Base):
    """OnlineServiceRequest Table Definition."""

    __tablename__ = "online_service_requests"

    request_id = Column(
        GUID(),
        ForeignKey("requests.id", ondelete="CASCADE"),
        primary_key=True,
    )
    meetup_latitude = Column(Float, nullable=False)
    meetup_longitude = Column(Float, nullable=False)

    request = relationship("Request", back_populates="online_service")

    def to_dict(self) -> dict[str, float]:
        return {
            "meetup_latitude": self.meetup_latitude,
            "meetup_longitude": self.meetup_longitude,
        }
