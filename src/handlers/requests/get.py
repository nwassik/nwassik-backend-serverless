from decimal import Decimal

from src.lib.responses import success, error
from src.lib.database import get_dynamodb_table_requests_connexion


def get_request(event, _):
    try:
        request_id = event.get("pathParameters", {}).get("request_id")
        db = get_dynamodb_table_requests_connexion()
        response = db.get_item(Key={"request_id": request_id})
        request = response.get("Item")
        if not request:
            return error("Request not found", 404)

        # Convert Decimal to float for JSON serialization
        for key, value in request.items():
            if isinstance(value, Decimal):
                request[key] = float(value)

        return success({"request": request})
    except Exception as e:
        return error(str(e))
