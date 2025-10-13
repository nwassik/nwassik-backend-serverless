from src.lib.responses import success, error
from src.lib.database import get_dynamodb_table_requests_connexion


def delete_request(event, _):
    try:
        request_id = event.get("pathParameters", {}).get("request_id")
        claims = event.get("requestContext").get("authorizer").get("claims")
        user_id = claims.get("sub")

        db = get_dynamodb_table_requests_connexion()

        # NOTE: Check user ownership on the request id to delete
        response = db.get_item(Key={"request_id": request_id})
        item = response.get("Item")
        if not item:
            return error("Request not found", status_code=404)
        if item.get("user_id") != user_id:
            return error(
                "Forbidden: you can only delete your own requests", status_code=403
            )

        # Delete the specific request from DynamoDB
        db.delete_item(Key={"request_id": request_id})

        return success(
            {"message": "Request deleted successfully", "request_id": request_id}
        )
    except Exception as e:
        return error(str(e))
