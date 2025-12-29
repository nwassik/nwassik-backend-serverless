"""Requests List Handler."""

from src.lib.responses import error, success
from src.repositories.request_repository import get_request_repository


def list_requests(event, _):  # noqa
    request_repo = get_request_repository()
    try:
        # Get query parameters for pagination
        query_params = event.get("queryStringParameters") or {}
        cursor = query_params.get("cursor")
        limit = int(query_params.get("limit", 20))
        request_type = query_params.get("type")

        # Get paginated results
        result = request_repo.list_of_requests(
            request_type=request_type,
            limit=limit,
            cursor=cursor,
        )

        # Convert requests to dicts for JSON response
        requests_data = [req.to_dict() for req in result["requests"]]

        return success({
            "requests": requests_data,
            "pagination": result["pagination"],
        })

    # TODO: need to hide backend errors to the end user, or at least send
    # a default "an error has occured", maybe identified with number
    except Exception as e:
        return error(str(e))
