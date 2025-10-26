from uuid import uuid4

from src.repositories.interfaces import FavoriteRepositoryInterface
from src.db.session import get_db_session

from sqlalchemy import desc

from src.models.favorite import Favorite
from uuid import UUID

from typing import List, Optional

_favorite_repo_instance = None


def get_favorite_repository() -> "FavoriteRepository":
    global _favorite_repo_instance
    if _favorite_repo_instance is None:
        _favorite_repo_instance = FavoriteRepository()
    return _favorite_repo_instance


class FavoriteRepository(FavoriteRepositoryInterface):
    """
    Concrete implementation of FavoriteRepositoryInterface using SQLAlchemy.
    Methods rely on get_db_session() context manager which commits on normal exit
    and rolls back on exception.
    """

    def create(self, user_id: UUID, request_id: UUID) -> Favorite:
        """
        Add a favorite for user -> request. If the favorite already exists,
        return the existing Favorite object (idempotent).
        """
        with get_db_session() as db:
            # Check existing first to provide idempotency and avoid IntegrityError
            existing = (
                db.query(Favorite)
                .filter(Favorite.user_id == user_id, Favorite.request_id == request_id)
                .first()
            )
            if existing:
                return existing

            favorite = Favorite(user_id=user_id, request_id=request_id)
            db.add(favorite)
            return favorite

    def get_by_id(self, favorite_id: UUID) -> Optional[Favorite]:
        with get_db_session() as db:
            return db.query(Favorite).filter(Favorite.id == favorite_id).first()

    def delete(self, request_id) -> bool:
        """
        Remove a favorite. Returns True whether a row was deleted or not (idempotent).
        """
        with get_db_session() as db:
            favorite = db.query(Favorite).filter(Favorite.id == request_id).first()
            if not favorite:  # Already removed
                return True
            db.delete(favorite)
            return True

    def list_user_favorites(self, user_id: UUID) -> List[Favorite]:
        """
        Return all favorites for a user, ordered by created_at DESC (most recent first).
        This intentionally returns the Favorite objects (with .request relationship available
        if your model defines it as eager/joined).
        """
        with get_db_session() as db:
            favorites = (
                db.query(Favorite)
                .filter(Favorite.user_id == user_id)
                .order_by(desc(Favorite.created_at))
                .all()
            )
            return favorites
