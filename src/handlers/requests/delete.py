from src.lib.responses import success, error
from src.repositories.request_repository import get_request_repository


def delete_request(event, _):
    request_repo = get_request_repository()
    try:
        request_id = event.get("pathParameters", {}).get("request_id")
        claims = event.get("requestContext").get("authorizer").get("claims")
        user_id = claims.get("sub")

        request = request_repo.get_by_id(request_id)

        if not request:
            return True
        if str(request.user_id) != user_id:
            return error(
                "Forbidden: you can only delete your own requests", status_code=403
            )

        request_repo.delete(request_id=request_id)

        return success(
            {"message": "Request deleted successfully", "request_id": request_id}
        )
    except Exception as e:
        return error(str(e))
