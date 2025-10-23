from datetime import date, datetime, timezone
from typing import Optional, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator
from enum import Enum


class RequestType(str, Enum):
    buy_and_deliver = "buy_and_deliver"
    pickup_and_deliver = "pickup_and_deliver"
    online_service = "online_service"


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
    due_date: Optional[datetime] = Field(None)
    request_type: RequestType

    title: str = Field(..., max_length=100)  # TODO: decide adequate length
    description: str = Field(..., max_length=500)  # TODO: decide adequate length

    # Product delivery locations
    pickup_latitude: Optional[float] = Field(None, ge=-90, le=90)
    pickup_longitude: Optional[float] = Field(None, ge=-180, le=180)
    dropoff_latitude: Optional[float] = Field(None, ge=-90, le=90)
    dropoff_longitude: Optional[float] = Field(None, ge=-180, le=180)

    # Service / meetup location
    meetup_latitude: Optional[float] = Field(None, ge=-90, le=90)
    meetup_longitude: Optional[float] = Field(None, ge=-180, le=180)

    @model_validator(mode="after")
    def validate_due_date(self):
        now_utc = datetime.now(timezone.utc)

        # Ensure due_date is timezone-aware and in the future
        if self.due_date is not None:
            if self.due_date.tzinfo is None:
                raise ValueError("due_date must be timezone-aware (UTC)")
            if self.due_date <= now_utc:
                raise ValueError("due_date must be in the future (UTC)")

        return self

    # -------------------------------
    # Conditional / cross-field validation
    # -------------------------------
    @model_validator(mode="after")
    def check_pickup_location(self):
        """
        Conditional validation for request types:
        - buy_and_deliver: dropoff location required
        - pickup_and_deliver: pickup + dropoff locations both required
        - online_service: meetup location required
        """
        r_type = self.request_type

        pickup_lat = self.pickup_latitude
        pickup_lon = self.pickup_longitude
        drop_off_lat = self.dropoff_latitude
        drop_off_lon = self.dropoff_latitude
        meetup_lat = self.meetup_latitude
        meetup_lon = self.meetup_longitude

        # buy & deliver check
        if r_type == RequestType.buy_and_deliver:
            if drop_off_lat is None or drop_off_lon is None:
                raise ValueError(
                    "dropoff_latitude and dropoff_latitude must be set for buy_and_deliver requests"
                )
            else:
                if any(
                    v is not None
                    for v in (pickup_lat, pickup_lon, meetup_lat, meetup_lon)
                ):
                    raise ValueError(
                        "pickup_latitude, pickup_longitude, meetup_latitude and meetup_longitude all must be None for buy_and_deliver requests"
                    )

        # pickup & deliver check
        elif r_type == RequestType.pickup_and_deliver:
            if any(
                v is None for v in (pickup_lat, pickup_lon, drop_off_lat, drop_off_lon)
            ):
                raise ValueError(
                    "pickup_latitude, pickup_longitude, dropoff_latitude and dropoff_latitude all must be set for pickup_and_deliver requests"
                )
            else:
                if any(v is not None for v in (meetup_lat, meetup_lon)):
                    raise ValueError(
                        "meetup_latitude and meetup_longitude must not be set for pickup_and_deliver requests"
                    )

        # online service check
        else:
            if any(v is None for v in (meetup_lat, meetup_lon)):
                raise ValueError(
                    "meetup_latitude and meetup_longitude must be set for online_service requests"
                )
            else:
                if any(
                    v is not None
                    for v in (pickup_lat, pickup_lon, drop_off_lat, drop_off_lon)
                ):
                    raise ValueError(
                        "pickup_latitude, pickup_longitude, dropoff_latitude and dropoff_latitude all must be None for online_service requests"
                    )

        return self


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
