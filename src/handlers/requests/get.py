from decimal import Decimal

from src.lib.responses import success, error
from src.lib.database import get_dynamodb_table_connexion

def get_request(event, context):
    try:
        # TODO: this should be the responsibility of api gateway, to respect raise error early, watch for this in other files
        # Get request ID from path
        request_id = event.get('pathParameters', {}).get('request_id')
        
        if not request_id:
            return error("Request ID is required", 400)
        
        db = get_dynamodb_table_connexion()
        
        
        response = db.get_item(
            Key={
                'pk': f'REQUEST#{request_id}',
                'sk': 'METADATA'
            }
        )
        
        request = response.get('Item')
        
        if not request:
            return error("Request not found", 404)

        # Convert Decimal to float for JSON serialization
        for key, value in request.items():
            if isinstance(value, Decimal):
                request[key] = float(value)

        return success({
            "request": request
        })
    except Exception as e:
        return error(str(e))
