import json


def health_check(event, context):
    """
    Simple health check Lambda function.

    Returns HTTP 200 with a JSON body indicating service status.
    """
    # TODO: Change this to real health check
    response = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"status": "ok", "message": "Service is healthy"}),
    }

    return response
