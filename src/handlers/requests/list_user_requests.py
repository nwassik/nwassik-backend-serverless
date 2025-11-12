from src.lib.responses import success, error
from src.repositories.request_repository import get_request_repository
from uuid import UUID


def list_user_requests(event, _):
    request_repo = get_request_repository()

    try:
        # NOTE: This is not necessarly the logged in user so there is no authorization check
        user_id = UUID(event.get("pathParameters", {}).get("user_id"))
        requests = request_repo.get_user_requests(user_id=user_id)
        return success(
            {
                "requests": [req.to_dict() for req in requests],
                "user_id": user_id,
                "total": len(requests),
            }
        )
    except Exception as e:
        return error(str(e))
