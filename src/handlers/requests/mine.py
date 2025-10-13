from decimal import Decimal

from src.lib.responses import success, error
from src.lib.database import get_dynamodb_table_requests_connexion
from boto3.dynamodb.conditions import Key


def list_my_requests(event, context):
    try:
        # TODO: Get real user_id from Cognito
        claims = event.get("requestContext").get("authorizer").get("claims")
        user_id = claims.get("sub")

        db = get_dynamodb_table_requests_connexion()

        # Query all requests for this user
        response = db.query(
            IndexName="UserRequestsGSI",
            KeyConditionExpression=Key("user_id").eq(user_id),
            ScanIndexForward=False,  # newest first
        )

        requests = response.get("Items", [])

        # TODO: Convert Decimal to float for JSON serialization
        # Need to unify it also: used in list + get
        for request in requests:
            for key, value in request.items():
                if isinstance(value, Decimal):
                    request[key] = float(value)

        return success(
            {"requests": requests, "user_id": user_id, "total": len(requests)}
        )
    except Exception as e:
        return error(str(e))
