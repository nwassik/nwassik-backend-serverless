from src.lib.responses import success, error

def get_request(event, context):
    # Get request ID from path
    request_id = event.get('pathParameters', {}).get('request_id')
    
    if not request_id:
        return error("Request ID is required", 400)
    
    # For now, return mock data
    return success({
        "request": {
            "id": request_id,
            "title": "Mock Request",
            "description": "This is a mock request"
        }
    })