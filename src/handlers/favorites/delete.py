"""Favorite Deletion Handler."""

from uuid import UUID

from src.lib.responses import error, success
from src.repositories.favorite_repository import get_favorite_repository


def delete_favorite(event, _):  # noqa
    favorite_repo = get_favorite_repository()
    try:
        favorite_id = UUID(event.get("pathParameters", {}).get("favorite_id"))
        # HTTP API JWT authorizer structure: requestContext.authorizer.jwt.claims
        claims = event["requestContext"]["authorizer"]["jwt"]["claims"]
        user_id = UUID(claims["sub"])

        favorite = favorite_repo.get_by_id(favorite_id=favorite_id)

        # NOTE: This is to be idempotent
        if not favorite:
            return success(
                {
                    "message": "Favorite deleted successfully",
                    "favorite_id": str(favorite_id),
                },
            )
        if favorite.user_id != user_id:
            return error("Forbidden: you can only delete your own favorites", status_code=403)

        favorite_repo.delete(favorite_id=favorite_id)

        return success(
            {
                "message": "Favorite deleted successfully",
                "favorite_id": str(favorite_id),
            },
        )
    except Exception as e:
        return error(str(e))
