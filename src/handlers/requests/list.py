from decimal import Decimal

from src.lib.responses import success, error
from src.lib.database import get_dynamodb_table_requests_connexion
from boto3.dynamodb.conditions import Key


def list_requests(event, _):
    try:
        db = get_dynamodb_table_requests_connexion()

        # TODO: Make sure timestamp makes sense, maybe someone is playing with the API
        # Validation also should be in API Gateway level as:
        # mandatory, integer and within fixed wide range
        timestamp_qs = int(event.get("queryStringParameters").get("from_timestamp"))

        # Query the AllRequestsGSI
        # FIXME: Here we have a hot partition, but for early phases that's OK
        response = db.query(
            IndexName="AllRequestsGSI",
            KeyConditionExpression=Key("ALL_REQUESTS").eq("ALL")
            & Key("due_date_ts").gt(Decimal(timestamp_qs)),
            Limit=20,
            ScanIndexForward=True,  # True -> ascending by due_date_ts
        )
        requests = response.get("Items", [])

        # TODO: Centralize this for code clarity. The get method uses the same pattern
        # Convert Decimal to float for JSON serialization
        for request in requests:
            for key, value in request.items():
                if isinstance(value, Decimal):
                    request[key] = float(value)

        return success({"requests": requests, "total": len(requests)})

    # TODO: need to hide backend errors to the end user, or at least send a default "an error has occured", maybe identified with number
    except Exception as e:
        return error(str(e))
