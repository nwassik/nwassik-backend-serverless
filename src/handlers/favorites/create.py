import json
from uuid import UUID

from src.lib.responses import success, error
from src.repositories.favorite_repository import get_favorite_repository


def create_favorite(event, _):
    favorite_repo = get_favorite_repository()

    # TODO: Put a limit on favorite items per user maybe 100
    try:
        claims = event.get("requestContext").get("authorizer").get("claims")
        user_id = UUID(claims.get("sub"))

        body = json.loads(event.get("body", "{}"))

        request_id = UUID(body.get("request_id"))

        # Add favorite (repository handles idempotance)
        favorite = favorite_repo.create(user_id=user_id, request_id=request_id)

        return success(
            {
                "message": "Favorite created successfully",
                "favorite_id": str(favorite.id),
            }
        )

    except Exception as e:
        return error(str(e))
