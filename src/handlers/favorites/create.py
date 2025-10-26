import json
from uuid import UUID

from src.lib.responses import success, error
from src.repositories.favorite_repository import get_favorite_repository


def create_favorite(event, _):
    favorite_repo = get_favorite_repository()

    try:
        claims = event.get("requestContext").get("authorizer").get("claims")
        user_id = UUID(claims.get("sub"))

        body = json.loads(event.get("body", "{}"))

        request_id_str = body.get("request_id")
        if not request_id_str:
            return error("Missing 'request_id' in body", 400)
        # Validate UUID format
        try:
            request_id = UUID(request_id_str)
        except (ValueError, TypeError):
            return error("Invalid 'request_id' format. Must be a valid UUID.", 400)

        # Add favorite (repository handles idempotance)
        favorite = favorite_repo.create(user_id=user_id, request_id=request_id)

        return success(
            {
                "message": "Favorite created successfully",
                "favorite_id": str(favorite.id),
                "request_id": str(favorite.request_id),
            }
        )

    except Exception as e:
        return error(str(e))
