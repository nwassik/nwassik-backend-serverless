from datetime import date, datetime, timezone
from typing import Optional, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator
from enum import Enum


class RequestType(str, Enum):
    delivery_only = "delivery_only"
    pickup_and_delivery = "pickup_and_delivery"


class LocationFilter(BaseModel):
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    radius_km: Optional[float] = Field(10.0, gt=0)

    @model_validator(mode="after")
    def validate_all_or_none(cls: type[Self], values: Self):
        lat, lng, radius = values.lat, values.lng, values.radius_km
        filled = [lat is not None, lng is not None, radius is not None]
        if any(filled) and not all(filled):
            raise ValueError(
                "All of lat, lng, and radius_km must be provided together."
            )
        return values


class RequestCreate(BaseModel):
    due_date_ts: int = Field(
        ge=int(datetime.now(timezone.utc).timestamp()),
        le=int(datetime(2027, 1, 1).timestamp()),
    )
    request_type: RequestType

    title: str = Field(..., max_length=255)
    description: str
    dropoff_latitude: float = Field(..., ge=-90, le=90)
    dropoff_longitude: float = Field(..., ge=-180, le=180)
    pickup_latitude: Optional[float] = Field(None, ge=-90, le=90)
    pickup_longitude: Optional[float] = Field(None, ge=-180, le=180)

    # -------------------------------
    # Conditional / cross-field validation
    # -------------------------------
    @model_validator(mode="after")
    def check_pickup_location(cls, values):
        r_type = values.request_type
        pickup_lat = values.pickup_latitude
        pickup_lon = values.pickup_longitude

        if r_type == RequestType.pickup_and_delivery:
            if pickup_lat is None or pickup_lon is None:
                raise ValueError(
                    "pickup_latitude and pickup_longitude must be set for pickup_and_delivery requests"
                )
        else:
            if pickup_lat is not None or pickup_lon is not None:
                raise ValueError(
                    "pickup_latitude and pickup_longitude must be None for delivery_only requests"
                )
        return values


class RequestOut(BaseModel):
    id: int
    request_type: RequestType
    title: str
    description: str
    dropoff_latitude: float
    dropoff_longitude: float
    pickup_latitude: Optional[float]
    pickup_longitude: Optional[float]
    due_date: Optional[date]
    user_id: int  # Not sure if this is useful
    username: str
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class RequestUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None)

    # dropoff_latitude: Optional[float] = Field(None, ge=-90, le=90)
    # dropoff_longitude: Optional[float] = Field(None, ge=-180, le=180)
    # pickup_latitude: Optional[float] = Field(None, ge=-90, le=90)
    # pickup_longitude: Optional[float] = Field(None, ge=-180, le=180)
    # due_date: Optional[date] = None

    @model_validator(mode="after")
    def check_setup_and_filled(cls, values):
        """
        Ensure at least one of title or description is provided.
        """
        title, description = values.title, values.description

        if title is None and description is None:
            raise ValueError(
                "At least one of 'title' or 'description' must be provided."
            )

        if values.title is not None and not values.title.strip():
            raise ValueError("Title cannot be empty or whitespace.")

        return values
