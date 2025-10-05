from src.lib.responses import success

def list_requests(event, context):
    # For now, return empty list
    return success({
        "requests": [],
        "total": 0
    })