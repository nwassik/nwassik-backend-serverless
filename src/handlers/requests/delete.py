from src.lib.responses import success, error

def delete_request(event, context):
    # Get request ID from path
    request_id = event.get('pathParameters', {}).get('request_id')
    
    if not request_id:
        return error("Request ID is required", 400)
    
    # For now, just return success
    return success({
        "message": "Request deleted",
        "request_id": request_id
    })