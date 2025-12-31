"""Request Repository."""

from uuid import UUID

from sqlalchemy import desc

from src.db.session import get_db_session
from src.models.favorite import Favorite
from src.repositories.interfaces import FavoriteRepositoryInterface

_favorite_repo_instance = None


def get_favorite_repository() -> "FavoriteRepository":
    """Get a request repository instance."""
    global _favorite_repo_instance  # noqa: PLW0603
    if _favorite_repo_instance is None:
        _favorite_repo_instance = FavoriteRepository()
    return _favorite_repo_instance


class FavoriteRepository(FavoriteRepositoryInterface):
    """Favorites Repository containing all necessary methods.

    Concrete implementation of FavoriteRepositoryInterface using SQLAlchemy.
    Methods rely on get_db_session() context manager which commits on normal exit
    and rolls back on exception.
    """

    def create(self, user_id: UUID, request_id: UUID) -> Favorite:
        """Create Favorite for User.

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

    def get_by_id(self, favorite_id: UUID) -> Favorite | None:
        with get_db_session() as db:
            return db.query(Favorite).filter(Favorite.id == favorite_id).first()

    def delete(self, favorite_id: UUID) -> bool:
        """Delete a Favorite by its ID.

        Returns Boolean whether a row was deleted or not (idempotent).
        """
        with get_db_session() as db:
            favorite = db.query(Favorite).filter(Favorite.id == favorite_id).first()
            if not favorite:  # Already removed
                return True
            db.delete(favorite)
            return True

    def list_user_favorites(self, user_id: UUID) -> list[Favorite]:
        """List a User's Favorites.

        Return all favorites for a user, ordered by created_at DESC (most recent first).
        This intentionally returns the Favorite objects (with .request relationship available
        if your model defines it as eager/joined).
        """
        with get_db_session() as db:
            return (
                db.query(Favorite)
                .filter(Favorite.user_id == user_id)
                .order_by(desc(Favorite.created_at))
                .all()
            )
