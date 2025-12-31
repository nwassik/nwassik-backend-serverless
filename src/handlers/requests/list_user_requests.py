"""User Requests List Handler."""

from uuid import UUID

from src.lib.responses import error, success
from src.repositories.request_repository import get_request_repository


def list_user_requests(event, _):  # noqa
    request_repo = get_request_repository()

    try:
        # NOTE: This is not necessarly the logged in user so there is no authorization check
        # TODO: Even though this works, the workflow is not natural. It currently returns an
        # empty list if the user does not exist (which is a workflow that shouldn't happen).
        # which also the same behaviour as a user who exists but that still didnt create requests
        # Simply return an error with value 'user do not exist'. or maybe this is useless...
        user_id = UUID(event.get("pathParameters", {}).get("user_id"))
        requests = request_repo.get_user_requests(user_id=user_id)
        return success(
            {
                "requests": [req.to_dict() for req in requests],
                "user_id": str(user_id),
                "total": len(requests),
            },
        )
    except Exception as e:
        return error(str(e))
