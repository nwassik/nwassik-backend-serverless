from abc import ABC, abstractmethod


from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from src.models.request import Request
from src.schemas.request import RequestCreate


# FIXME: For every method should return whether Request or Union of sub types
class RequestRepositoryInterface(ABC):
    @abstractmethod
    def create(self, user_id: UUID, request_data: RequestCreate) -> Request:
        """Create a new request with its specific subtype"""
        pass

    @abstractmethod
    def get_by_id(self, request_id: UUID) -> Optional[Request]:
        """Get a request by its ID"""
        pass

    # TODO: @abstractmethod
    def get_batch_from_last_item(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Request]:
        """Get a batch of requests with pagination"""
        pass

    # TODO: @abstractmethod
    def get_batch_from_due_date(
        self, start_due_date: datetime, limit: int = 20
    ) -> List[Request]:
        """Get a batch of requests starting from specific due date"""
        pass

    # TODO: @abstractmethod
    def update(self, request_id: UUID, data: Dict[str, Any]) -> Optional[Request]:
        """Update request fields"""
        pass

    @abstractmethod
    def delete(self, request_id: UUID) -> bool:
        """Delete a request by ID"""
        pass
