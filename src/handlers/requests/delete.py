"""Request Deletion Handler."""

from uuid import UUID

from src.lib.responses import error, success
from src.repositories.request_repository import get_request_repository


def delete_request(event, _):  # noqa
    request_repo = get_request_repository()
    try:
        request_id = UUID(event.get("pathParameters", {}).get("request_id"))
        # HTTP API JWT authorizer structure: requestContext.authorizer.jwt.claims
        claims = event["requestContext"]["authorizer"]["jwt"]["claims"]
        user_id = UUID(claims["sub"])

        request = request_repo.get_by_id(request_id)

        # NOTE: This is done to be idempotent
        if not request:
            return success(
                data={
                    "message": "Request deleted successfully",
                    "request_id": str(request_id),
                },
                status_code=204,
            )

        if request.user_id != user_id:
            return error("Forbidden: you can only delete your own requests", status_code=403)

        request_repo.delete(request_id=request_id)

        return success(
            data={
                "message": "Request deleted successfully",
                "request_id": str(request_id),
            },
            status_code=204,
        )
    except Exception as e:
        return error(str(e))
