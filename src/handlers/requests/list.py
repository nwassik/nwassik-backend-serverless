"""Requests List Handler."""

from src.lib.responses import error, success
from src.repositories.request_repository import get_request_repository


def list_requests(event, _):  # noqa
    request_repo = get_request_repository()
    try:
        requests = request_repo.list_of_requests()

        return success({"requests": requests, "total": len(requests)})

    # TODO: need to hide backend errors to the end user, or at least send
    # a default "an error has occured", maybe identified with number
    except Exception as e:
        return error(str(e))
