from src.lib.responses import success, error
from src.repositories.request_repository import get_request_repository


def list_user_requests(event, context):
    request_repo = get_request_repository()

    try:
        # NOTE: This is not necessarly the logged in user
        user_id = event.get("pathParameters", {}).get("user_id")
        requests = request_repo.get_user_requests(user_id=user_id)
        return success(
            {
                "requests": requests,
                "user_id": user_id,
                "total": len(requests),
            }
        )
    except Exception as e:
        return error(str(e))
