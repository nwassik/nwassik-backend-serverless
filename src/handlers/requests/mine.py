from src.lib.responses import success

def list_my_requests(event, context):
    # For now, return empty list with mock user
    user_id = "mock-user-id"
    
    return success({
        "requests": [],
        "user_id": user_id
    })