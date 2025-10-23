import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    Enum,
    ForeignKey,
)
from .base import Base
from src.schemas.request import RequestType
from .types import GUID


class Request(Base):
    __tablename__ = "requests"

    # default value is Python side generated and not DB Side
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False)

    request_type = Column(Enum(RequestType), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)

    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now)


class BuyAndDeliverRequest(Base):
    __tablename__ = "buy_and_deliver_requests"

    request_id = Column(
        GUID(),
        ForeignKey("requests.id", ondelete="CASCADE"),
        primary_key=True,
    )
    dropoff_latitude = Column(Float, nullable=False)
    dropoff_longitude = Column(Float, nullable=False)


class PickupAndDeliverRequest(Base):
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


class OnlineServiceRequest(Base):
    __tablename__ = "online_service_requests"

    request_id = Column(
        GUID(),
        ForeignKey("requests.id", ondelete="CASCADE"),
        primary_key=True,
    )
    meetup_latitude = Column(Float, nullable=False)
    meetup_longitude = Column(Float, nullable=False)
