from enum import Enum

class RequestType(str, Enum):
    delivery_only = "delivery_only"
    pickup_and_delivery = "pickup_and_delivery"
