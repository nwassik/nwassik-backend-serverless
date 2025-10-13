import json
from src.lib.responses import success, error
from src.lib.database import get_dynamodb_table_requests_connexion
from src.schemas.request import RequestUpdate

from decimal import Decimal
from datetime import datetime, timezone


def update_request(event, _):
    try:
        # TODO: Get real user_id from Cognito
        claims = event.get("requestContext").get("authorizer").get("claims")
        user_id = claims.get("sub")
        request_id = event.get("pathParameters", {}).get("request_id")

        body = json.loads(event.get("body", "{}"))
        request_update = RequestUpdate(body)

        db = get_dynamodb_table_requests_connexion()

        response = db.get_item(Key={"request_id": request_id})
        request = response.get("Item")
        if not request:
            return error("Request not found", 404)

        # NOTE: Check user ownership on the request id to delete
        if request.get("user_id") != user_id:
            return error("Not authorized to update this request", 403)

        # Build update expression from provided fields
        update_data = request_update.model_dump(exclude_unset=True)

        # Prepare DynamoDB UpdateExpression
        update_expr = "SET " + ", ".join(f"{k} = :{k}" for k in update_data.keys())
        expr_attr_values = {f":{k}": v for k, v in update_data.items()}

        db.update_item(
            Key={"request_id": request_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_attr_values,
        )

        return success(
            {"message": "Request updated successfully", "request_id": request_id}
        )

    except Exception as e:
        return error(str(e))
