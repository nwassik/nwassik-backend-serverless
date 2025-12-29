"""Pydantic schemas for service request validation and serialization."""

from datetime import UTC, datetime
from enum import Enum
from typing import Self
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class RequestType(str, Enum):
    """Types of service requests available in the marketplace."""

    BUY_AND_DELIVER = "buy_and_deliver"
    PICKUP_AND_DELIVER = "pickup_and_deliver"
    ONLINE_SERVICE = "online_service"


class RequestCreate(BaseModel):
    """Schema for creating a new service request."""

    due_date: datetime | None = Field(None)
    type: RequestType

    title: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)

    # Product delivery locations
    pickup_latitude: float | None = Field(None, ge=-90, le=90)
    pickup_longitude: float | None = Field(None, ge=-180, le=180)
    dropoff_latitude: float | None = Field(None, ge=-90, le=90)
    dropoff_longitude: float | None = Field(None, ge=-180, le=180)

    # Service / meetup location
    meetup_latitude: float | None = Field(None, ge=-90, le=90)
    meetup_longitude: float | None = Field(None, ge=-180, le=180)

    @model_validator(mode="after")
    def validate_due_date(self) -> Self:
        """Ensure due date is timezone-aware and set in the future."""
        now_utc = datetime.now(UTC)

        # Ensure due_date is timezone-aware and in the future
        if self.due_date is not None:
            if self.due_date.tzinfo is None:
                exception_msg = "due_date must be timezone-aware (UTC)"
                raise ValueError(exception_msg)
            if self.due_date <= now_utc:
                exception_msg = "due_date must be in the future (UTC)"
                raise ValueError(exception_msg)

        return self

    # -------------------------------
    # Conditional / cross-field validation
    # -------------------------------
    @model_validator(mode="after")
    def check_location(self) -> Self:
        """Check location structure.

        - BUY_AND_DELIVER: dropoff location required
        - PICKUP_AND_DELIVER: pickup + dropoff locations both required
        - ONLINE_SERVICE: meetup location required
        """
        r_type = self.type

        pickup_lat = self.pickup_latitude
        pickup_lon = self.pickup_longitude
        drop_off_lat = self.dropoff_latitude
        drop_off_lon = self.dropoff_longitude
        meetup_lat = self.meetup_latitude
        meetup_lon = self.meetup_longitude

        # buy & deliver check
        if r_type == RequestType.BUY_AND_DELIVER:
            if drop_off_lat is None or drop_off_lon is None:
                exception_msg = (
                    "dropoff_latitude and dropoff_longitude must be set for "
                    "BUY_AND_DELIVER requests"
                )
                raise ValueError(exception_msg)
            if any(v is not None for v in (pickup_lat, pickup_lon, meetup_lat, meetup_lon)):
                exception_msg = (
                    "pickup_latitude, pickup_longitude, meetup_latitude and "
                    "meetup_longitude all must be None for BUY_AND_DELIVER requests"
                )
                raise ValueError(exception_msg)

        # pickup & deliver check
        elif r_type == RequestType.PICKUP_AND_DELIVER:
            if any(v is None for v in (pickup_lat, pickup_lon, drop_off_lat, drop_off_lon)):
                exception_msg = (
                    "pickup_latitude, pickup_longitude, dropoff_latitude and "
                    "dropoff_longitude all must be set for PICKUP_AND_DELIVER requests"
                )
                raise ValueError(exception_msg)
            if any(v is not None for v in (meetup_lat, meetup_lon)):
                exception_msg = (
                    "meetup_latitude and meetup_longitude must not be set for "
                    "PICKUP_AND_DELIVER requests"
                )
                raise ValueError(exception_msg)

        # online service check
        else:
            if any(v is None for v in (meetup_lat, meetup_lon)):
                exception_msg = (
                    "meetup_latitude and meetup_longitude must be set for ONLINE_SERVICE requests"
                )
                raise ValueError(exception_msg)
            if any(v is not None for v in (pickup_lat, pickup_lon, drop_off_lat, drop_off_lon)):
                exception_msg = (
                    "pickup_latitude, pickup_longitude, dropoff_latitude and "
                    "dropoff_longitude all must be None for ONLINE_SERVICE requests"
                )
                raise ValueError(exception_msg)

        return self


class BaseRequest(BaseModel):
    """Base schema for request responses with common fields."""

    id: UUID
    user_id: UUID
    type: RequestType
    title: str
    description: str | None = None
    due_date: datetime | None = None
    created_at: datetime


class BuyAndDeliverRequest(BaseRequest):
    """Request for buying an item abroad and delivering it to a specific location."""

    dropoff_latitude: float
    dropoff_longitude: float


class PickupAndDeliverRequest(BaseRequest):
    """Request for picking up an item from one location and delivering it to another."""

    pickup_latitude: float
    pickup_longitude: float
    dropoff_latitude: float
    dropoff_longitude: float


class OnlineServiceRequest(BaseRequest):
    """Request for purchasing an online service with a meetup location for transaction."""

    meetup_latitude: float
    meetup_longitude: float


class RequestUpdate(BaseModel):
    """Schema for updating an existing request's title or description."""

    title: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=500)

    @model_validator(mode="after")
    def check_setup_and_filled(self) -> Self:
        """Ensure at least one of title or description is provided."""
        if self.title is None and self.description is None:
            exception_msg = "At least one of 'title' or 'description' must be provided."
            raise ValueError(exception_msg)

        return self


class LocationFilter(BaseModel):
    """Filter requests by geographic location and radius."""

    lat: float | None = Field(None, ge=-90, le=90)
    lng: float | None = Field(None, ge=-180, le=180)
    radius_km: float | None = Field(10.0, gt=0)

    @model_validator(mode="after")
    def validate_all_or_none(self) -> Self:
        """Ensure all location fields are provided together or none at all."""
        lat, lng, radius = self.lat, self.lng, self.radius_km
        filled = [lat is not None, lng is not None, radius is not None]
        if any(filled) and not all(filled):
            exception_msg = "All of lat, lng, and radius_km must be provided together."
            raise ValueError(exception_msg)
        return self
