import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from src.lib.responses import success, error
from src.schemas.request import RequestCreate, RequestType
from src.lib.database import get_dynamodb_table_requests_connexion


def create_request(event, _):
    try:
        body = json.loads(event.get("body", "{}"))

        # NOTE: Validation could have been outside of Lambda and at API Gateway level,
        # for faster error response and no Lambda execution on schema validation failure,
        # but I need dynamic cross-attributes check which is not possible in API Gateway.
        # Only static stuff is supported for now in API Gateway
        request_data = RequestCreate.model_validate(body)

        claims = event.get("requestContext").get("authorizer").get("claims")
        user_id = claims.get("sub")
        db = get_dynamodb_table_requests_connexion()

        # FIXME: Need to limit number of requests created by user for spam.
        # Maximum 20 requests should be allowed at the same time
        # He needs to delete some of the old if he has already capped out
        request_id = str(uuid.uuid4())

        request = {
            "request_id": request_id,
            "user_id": user_id,
            # TODO: Make due date flexible with no due_date necessary
            # due date for now is rigid/mandatory, that's a good use case to start with
            "due_date_ts": request_data.due_date_ts,
            "request_type": request_data.request_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "title": request_data.title,
            "description": request_data.description,
            "dropoff_latitude": Decimal(str(request_data.dropoff_latitude)),
            "dropoff_longitude": Decimal(str(request_data.dropoff_longitude)),
            "ALL_REQUESTS": "ALL",
        }

        if request_data.request_type is RequestType.pickup_and_delivery:
            request["pickup_latitude"] = Decimal(str(request_data.pickup_latitude))
            request["pickup_longitude"] = Decimal(str(request_data.pickup_longitude))

        db.put_item(Item=request)

        return success(
            {
                "message": "Request created successfully",
                "request_id": request_id,
            }
        )
    except Exception as e:
        return error(str(e))
