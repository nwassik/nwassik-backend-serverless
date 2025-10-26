from src.lib.responses import success, error
from src.repositories.request_repository import get_request_repository


def get_request(event, _):
    request_repo = get_request_repository()
    try:
        request_id = event.get("pathParameters", {}).get("request_id")
        request = request_repo.get_by_id(request_id=request_id)

        if not request:
            return error("Request not found", 404)

        return success({"request": request.to_dict()})
    except Exception as e:
        return error(str(e))
