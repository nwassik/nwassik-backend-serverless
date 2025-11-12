from src.lib.responses import success, error
from src.repositories.favorite_repository import get_favorite_repository
from uuid import UUID


def list_user_favorites(event, _):
    favorite_repo = get_favorite_repository()

    try:
        claims = event.get("requestContext").get("authorizer").get("claims")
        user_id = UUID(claims.get("sub"))

        favorites = favorite_repo.list_user_favorites(user_id=user_id)
        return success(
            {
                "requests": [fav.to_dict() for fav in favorites],
                "user_id": user_id,
                "total": len(favorites),
            }
        )
    except Exception as e:
        return error(str(e))
