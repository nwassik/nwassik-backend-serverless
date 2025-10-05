import json
import uuid
from datetime import datetime, timezone

from src.lib.responses import success, error
from src.schemas.request import RequestCreate
from src.enums import RequestType
from src.lib.database import get_dynamodb_table_connexion

def create_request(event, context):
    try:
        # HTTP Validation
        body = json.loads(event.get('body', '{}'))
        db = get_dynamodb_table_connexion()
        request_data = RequestCreate(**body)
        
        # Business Validation
        if request_data.request_type == RequestType.pickup_and_delivery:
            if request_data.pickup_latitude is None or request_data.pickup_longitude is None:
                return error("Pickup location is required for 'pickup_and_delivery' requests", 400)
        

        # Business logic (everything in handler)
        # Get user from Cognito (mock for now)
        # Business logic (everything in handler)
        user_id = "mock-user-id"
        request_id = str(uuid.uuid4())
        

        request = {
            'pk': f'REQUEST#{request_id}',
            'sk': 'METADATA',
            
            'request_id': request_id,
            'user_id': user_id,
            'request_type': request_data.request_type,
            'title': request_data.title,
            'description': request_data.description,
            'due_date': request_data.due_date.isoformat() if request_data.due_date else None,

            'dropoff_latitude': request_data.dropoff_latitude,
            'dropoff_longitude': request_data.dropoff_longitude,
            'pickup_latitude': request_data.pickup_latitude,
            'pickup_longitude': request_data.pickup_longitude,
            
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        db.put_item(Item=request)


        return success({
            "message": "Request created successfully",
            "request_id": request_id,
        })
    except Exception as e:
        return error(str(e))