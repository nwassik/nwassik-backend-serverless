import json
from src.lib.responses import success, error
from src.lib.database import get_dynamodb_table_connexion
from src.schemas.request import RequestUpdate

from decimal import Decimal
from datetime import datetime, timezone

def update_request(event, context):
    try:
        request_id = event.get('pathParameters', {}).get('request_id')
        
        if not request_id:
            return error("Request ID is required", 400)
        
        body = json.loads(event.get('body', '{}'))
        request_update = RequestUpdate(**body)
        db = get_dynamodb_table_connexion()
        
        # TODO: Get real user_id from Cognito
        user_id = "mock-user-id"
        
        # Check if request exists and belongs to user
        response = db.get_item(
            Key={
                'pk': f'REQUEST#{request_id}',
                'sk': 'METADATA'
            }
        )
        
        request = response.get('Item')
        if not request:
            return error("Request not found", 404)
        
        if request.get('user_id') != user_id:
            return error("Not authorized to update this request", 403)
        
        # Build update expression from provided fields
        update_data = request_update.model_dump(exclude_unset=True)
        
        if not update_data:
            return error("No fields to update", 400)
        
        # Convert floats to Decimal for DynamoDB
        decimal_fields = ['dropoff_latitude', 'dropoff_longitude', 'pickup_latitude', 'pickup_longitude']
        for field in decimal_fields:
            if field in update_data and update_data[field] is not None:
                update_data[field] = Decimal(str(update_data[field]))
        
        # Convert due_date to string
        if 'due_date' in update_data and update_data['due_date']:
            update_data['due_date'] = update_data['due_date'].isoformat()
        
        # Build DynamoDB update expression
        update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in update_data.keys()])
        expression_attribute_names = {f"#{k}": k for k in update_data.keys()}
        expression_attribute_values = {f":{k}": v for k, v in update_data.items()}
        
        # Add updated_at timestamp
        update_expression += ", #updated_at = :updated_at"
        expression_attribute_names["#updated_at"] = "updated_at"
        expression_attribute_values[":updated_at"] = datetime.now(timezone.utc).isoformat()
        
        # Perform update
        db.update_item(
            Key={
                'pk': f'REQUEST#{request_id}',
                'sk': 'METADATA'
            },
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW"
        )
        
        return success({
            "message": "Request updated successfully",
            "request_id": request_id
        })
        
    except Exception as e:
        return error(str(e))