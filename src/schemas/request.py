from datetime import date, datetime
from typing import Optional, Self
import sys

from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.enums import RequestType

class LocationFilter(BaseModel):
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    radius_km: Optional[float] = Field(10.0, gt=0)

    @model_validator(mode="after")
    def validate_all_or_none(cls: type[Self], values: Self):
        lat, lng, radius = values.lat, values.lng, values.radius_km
        filled = [lat is not None, lng is not None, radius is not None]
        if any(filled) and not all(filled):
            raise ValueError("All of lat, lng, and radius_km must be provided together.")
        return values

class RequestCreate(BaseModel):
    request_type: RequestType = RequestType.delivery_only
    title: str = Field(..., max_length=255)
    description: str

    dropoff_latitude: float = Field(..., ge=-90, le=90)
    dropoff_longitude: float = Field(..., ge=-180, le=180)
    pickup_latitude: Optional[float] = Field(None, ge=-90, le=90)
    pickup_longitude: Optional[float] = Field(None, ge=-180, le=180)

    due_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


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
    description: Optional[str] = None
    dropoff_latitude: Optional[float] = Field(None, ge=-90, le=90)
    dropoff_longitude: Optional[float] = Field(None, ge=-180, le=180)
    pickup_latitude: Optional[float] = Field(None, ge=-90, le=90)
    pickup_longitude: Optional[float] = Field(None, ge=-180, le=180)
    due_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
