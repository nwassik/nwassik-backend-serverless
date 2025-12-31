"""Favorite Creation Handler."""

import json
from uuid import UUID

from src.lib.responses import error, success
from src.repositories.favorite_repository import get_favorite_repository
from src.repositories.request_repository import get_request_repository


def create_favorite(event, _):  # noqa
    favorite_repo = get_favorite_repository()
    request_repo = get_request_repository()

    # TODO: Put a limit on favorite items per user maybe 100
    try:
        # HTTP API JWT authorizer structure: requestContext.authorizer.jwt.claims
        claims = event["requestContext"]["authorizer"]["jwt"]["claims"]
        user_id = UUID(claims["sub"])

        body = json.loads(event.get("body", "{}"))

        request_id = UUID(body.get("request_id"))
        request = request_repo.get_by_id(request_id=request_id)

        if not request:
            return error("Request not found", 404)

        # Add favorite (repository handles idempotance)
        favorite = favorite_repo.create(user_id=user_id, request_id=request_id)

        return success(
            {
                "message": "Favorite created successfully",
                "favorite_id": str(favorite.id),
            },
        )

    except Exception as e:
        return error(str(e))
