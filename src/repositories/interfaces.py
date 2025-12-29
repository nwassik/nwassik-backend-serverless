"""Repositories Interfaces."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from uuid import UUID

from src.models.favorite import Favorite
from src.models.request import Request
from src.schemas.request import RequestCreate


# FIXME: For every method should return whether Request or Union of sub types
class RequestRepositoryInterface(ABC):  # noqa: D101
    @abstractmethod
    def create(self, user_id: UUID, request_data: RequestCreate) -> Request:
        """Create a new request with its specific subtype."""

    @abstractmethod
    def get_by_id(self, request_id: UUID) -> Request | None:
        """Get a request by its ID."""

    @abstractmethod
    def get_user_requests(self, user_id: UUID) -> list[Request]:
        """Get requests of a user."""

    # TODO: @abstractmethod
    def get_batch_from_last_item(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Request]:
        """Get a batch of requests with pagination."""

    # TODO: @abstractmethod
    def get_batch_from_due_date(self, start_due_date: datetime, limit: int = 20) -> list[Request]:
        """Get a batch of requests starting from specific due date."""

    @abstractmethod
    def update(self, request_id: UUID, data: dict[str, Any]) -> Request | None:
        """Update request fields."""

    @abstractmethod
    def delete(self, request_id: UUID) -> bool:
        """Delete a request by ID."""


class FavoriteRepositoryInterface(ABC):
    """Interface for managing user favorites."""

    @abstractmethod
    def add(self, user_id: UUID, request_id: UUID) -> Favorite:
        """Add a new favorite for a user."""

    @abstractmethod
    def delete(self, user_id: UUID, request_id: UUID) -> bool:
        """Remove a favorite by user and request."""

    @abstractmethod
    def is_favorite(self, user_id: UUID, request_id: UUID) -> bool:
        """Check if a given request is favorited by a specific user."""

    @abstractmethod
    def list_user_favorites(self, user_id: UUID) -> list[Favorite]:
        """List all favorites for a given user with no pagination."""
