from src.lib.responses import success, error
from src.lib.database import get_dynamodb_table_connexion

def delete_request(event, context):
    try:
        request_id = event.get('pathParameters', {}).get('request_id')
        
        if not request_id:
            return error("Request ID is required", 400)
        
        db = get_dynamodb_table_connexion()
        
        # Delete the specific request from DynamoDB
        db.delete_item(
            Key={
                'pk': f'REQUEST#{request_id}',
                'sk': 'METADATA'
            }
        )
        
        return success({
            "message": "Request deleted successfully",
            "request_id": request_id
        })
    except Exception as e:
        return error(str(e))