"""Favorite List Handler."""

from uuid import UUID

from src.lib.responses import error, success
from src.repositories.favorite_repository import get_favorite_repository


def list_user_favorites(event, _):  # noqa
    favorite_repo = get_favorite_repository()

    try:
        # HTTP API JWT authorizer structure: requestContext.authorizer.jwt.claims
        claims = event["requestContext"]["authorizer"]["jwt"]["claims"]
        user_id = UUID(claims["sub"])

        favorites = favorite_repo.list_user_favorites(user_id=user_id)
        return success(
            {
                "favorites": [fav.to_dict() for fav in favorites],
                "user_id": str(user_id),
                "total": len(favorites),
            }
        )
    except Exception as e:
        return error(str(e))
