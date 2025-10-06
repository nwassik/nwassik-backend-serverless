from decimal import Decimal

from src.lib.responses import success, error
from src.lib.database import get_dynamodb_table_connexion

def list_my_requests(event, context):
    try:
        # TODO: Get real user_id from Cognito
        user_id = "mock-user-id"
        
        db = get_dynamodb_table_connexion()
        
        # Query all requests for this user
        response = db.scan(
            FilterExpression='user_id = :user_id',
            ExpressionAttributeValues={
                ':user_id': user_id
            }
        )
        
        requests = response.get('Items', [])
        
        # Convert Decimal to float for JSON serialization
        for request in requests:
            for key, value in request.items():
                if isinstance(value, Decimal):
                    request[key] = float(value)

        return success({
            "requests": requests,
            "user_id": user_id,
            "total": len(requests)
        })
    except Exception as e:
        return error(str(e))