"""Request Update Handler."""

import json
from uuid import UUID

from src.lib.responses import error, success
from src.repositories.request_repository import get_request_repository
from src.schemas.request import RequestUpdate


def update_request(event, _):  # noqa
    request_repo = get_request_repository()
    try:
        claims = event.get("requestContext").get("authorizer").get("claims")
        user_id = UUID(claims.get("sub"))
        request_id = UUID(event.get("pathParameters", {}).get("request_id"))

        request = request_repo.get_by_id(request_id=request_id)

        if not request:
            return error("Request not found", 404)

        if request.user_id != user_id:
            return error("Not authorized to update this request", 403)

        body = json.loads(event.get("body", "{}"))
        request_update: RequestUpdate = RequestUpdate(body)

        request_repo.update(request_id=request_id, request_update=request_update)

        return success({"message": "Request updated successfully", "request_id": request_id})

    except Exception as e:
        return error(str(e))
