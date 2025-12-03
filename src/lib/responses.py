"""Common responses."""

import json
from typing import Any


def success(
    data: dict[str, Any],
    extra_headers: dict[str, str] | None,
    status_code: int = 200,
) -> dict[str, Any]:
    """Wrap success object."""
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json", **(extra_headers or {})},
        "body": json.dumps(data),
    }


def error(
    message: dict[str, Any],
    status_code: int = 400,
) -> dict[str, Any]:
    """Wrap error object."""
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": message}),
    }
