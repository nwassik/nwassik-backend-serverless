from typing import Optional
from datetime import datetime
from enum import Enum
from src.models.base import BaseModel

class RequestType(str, Enum):
    DELIVERY = "delivery"
    PICKUP_DELIVERY = "pickup_delivery"

class Request(BaseModel):
    request_id: str
    request_type: RequestType
    title: str
    description: str
    due_date: Optional[str] = None
    
    dropoff_latitude: float
    dropoff_longitude: float
    pickup_latitude: Optional[float] = None
    pickup_longitude: Optional[float] = None
    
    user_id: str
    created_at: str
    updated_at: str
    
    @property
    def pk(self):
        return f"REQUEST#{self.request_id}"
    
    @property
    def sk(self):
        return f"METADATA#{self.request_id}"