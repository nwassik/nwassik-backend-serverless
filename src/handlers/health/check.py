"""Health Check Module."""

import json
from typing import Any


def health_check(event, context) -> dict[str, Any]:  # noqa: ANN001, ARG001
    """Check Lambda Functions Dummy."""
    # TODO: Change this to real health check
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"status": "ok", "message": "Service is healthy"}),
    }
