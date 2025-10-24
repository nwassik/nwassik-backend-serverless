import json
from src.lib.responses import success, error
from src.schemas.request import RequestCreate
from src.repositories.request_repository import get_request_repository
from uuid import UUID


def create_request(event, _):
    request_repo = get_request_repository()
    try:
        body = json.loads(event.get("body", "{}"))

        # NOTE: Validation could have been outside of Lambda and at API Gateway level,
        # for faster error response and no Lambda execution on schema validation failure,
        # but I need dynamic cross attributes check which is not possible in API Gateway.
        # Only static stuff is supported for now in API Gateway
        input_request: RequestCreate = RequestCreate.model_validate(body)

        claims = event.get("requestContext").get("authorizer").get("claims")
        user_id = claims.get("sub")
        # FIXME: Need to limit number of requests created by user for spam.
        # Maximum 20 requests should be allowed at the same time
        # He needs to delete some of the old one if he has already capped out
        request = request_repo.create(
            user_id=UUID(user_id), input_request=input_request
        )

        return success(
            {
                "message": "Request created successfully",
                "request_id": str(request.id),
            }
        )
    except Exception as e:
        return error(str(e))
