"""Request Creation Handler."""

import json
from uuid import UUID

from config import MAX_USER_CREATED_REQUESTS
from src.lib.responses import error, success
from src.repositories.request_repository import get_request_repository
from src.schemas.request import RequestCreate


def create_request(event, _):  # noqa
    request_repo = get_request_repository()
    try:
        claims = event.get("requestContext").get("authorizer").get("claims")
        user_id = UUID(claims.get("sub"))

        # NOTE: Fail early
        if len(request_repo.get_user_requests(user_id=user_id)) >= MAX_USER_CREATED_REQUESTS:
            raise Exception("Too many requests created")  # noqa: TRY301

        body = json.loads(event.get("body", "{}"))

        # NOTE: Validation could have been outside of Lambda, at API Gateway level,
        # for faster error response and no Lambda execution on schema validation failure,
        # but I need dynamic cross attributes check which is not possible in API Gateway.
        # Only static stuff is supported for now in API Gateway
        input_request: RequestCreate = RequestCreate.model_validate(body)

        request = request_repo.create(
            user_id=UUID(user_id),
            input_request=input_request,
        )

        return success(
            {
                "message": "Request created successfully",
                "request_id": str(request.id),
            },
        )
    except Exception as e:
        return error(str(e))
