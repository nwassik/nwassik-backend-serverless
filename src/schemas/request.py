from datetime import datetime, timezone
from typing import Optional, Self, Union
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator
from enum import Enum


class RequestType(str, Enum):
    BUY_AND_DELIVER = "buy_and_deliver"
    PICKUP_AND_DELIVER = "pickup_and_deliver"
    ONLINE_SERVICE = "online_service"


class RequestCreate(BaseModel):
    due_date: Optional[datetime] = Field(None)
    type: RequestType

    title: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)

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
    def check_location(self):
        """
        Conditional validation for request types:
        - BUY_AND_DELIVER: dropoff location required
        - PICKUP_AND_DELIVER: pickup + dropoff locations both required
        - ONLINE_SERVICE: meetup location required
        """
        r_type = self.type

        pickup_lat = self.pickup_latitude
        pickup_lon = self.pickup_longitude
        drop_off_lat = self.dropoff_latitude
        drop_off_lon = self.dropoff_latitude
        meetup_lat = self.meetup_latitude
        meetup_lon = self.meetup_longitude

        # buy & deliver check
        if r_type == RequestType.BUY_AND_DELIVER:
            if drop_off_lat is None or drop_off_lon is None:
                raise ValueError(
                    "dropoff_latitude and dropoff_latitude must be set for BUY_AND_DELIVER requests"
                )
            else:
                if any(
                    v is not None
                    for v in (pickup_lat, pickup_lon, meetup_lat, meetup_lon)
                ):
                    raise ValueError(
                        "pickup_latitude, pickup_longitude, meetup_latitude and meetup_longitude all must be None for BUY_AND_DELIVER requests"
                    )

        # pickup & deliver check
        elif r_type == RequestType.PICKUP_AND_DELIVER:
            if any(
                v is None for v in (pickup_lat, pickup_lon, drop_off_lat, drop_off_lon)
            ):
                raise ValueError(
                    "pickup_latitude, pickup_longitude, dropoff_latitude and dropoff_latitude all must be set for PICKUP_AND_DELIVER requests"
                )
            else:
                if any(v is not None for v in (meetup_lat, meetup_lon)):
                    raise ValueError(
                        "meetup_latitude and meetup_longitude must not be set for PICKUP_AND_DELIVER requests"
                    )

        # online service check
        else:
            if any(v is None for v in (meetup_lat, meetup_lon)):
                raise ValueError(
                    "meetup_latitude and meetup_longitude must be set for ONLINE_SERVICE requests"
                )
            else:
                if any(
                    v is not None
                    for v in (pickup_lat, pickup_lon, drop_off_lat, drop_off_lon)
                ):
                    raise ValueError(
                        "pickup_latitude, pickup_longitude, dropoff_latitude and dropoff_latitude all must be None for ONLINE_SERVICE requests"
                    )

        return self


class BaseRequest(BaseModel):
    id: UUID
    user_id: UUID
    type: RequestType
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None  # Add this
    created_at: datetime

    # model_config = ConfigDict(
    #     from_attributes=True,  # ✅ Allow ORM objects
    #     json_encoders={
    #         datetime: lambda v: v.isoformat() + "Z",
    #         UUID: str,
    #     },
    # )


class BuyAndDeliverRequest(BaseRequest):
    dropoff_latitude: float
    dropoff_longitude: float


class PickupAndDeliverRequest(BaseRequest):
    pickup_latitude: float
    pickup_longitude: float
    dropoff_latitude: float
    dropoff_longitude: float


class OnlineServiceRequest(BaseRequest):
    meetup_latitude: float
    meetup_longitude: float


CompleteRequest = Union[
    BuyAndDeliverRequest,
    PickupAndDeliverRequest,
    OnlineServiceRequest,
]


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
