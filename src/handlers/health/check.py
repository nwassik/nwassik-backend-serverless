import json
import os
from datetime import datetime, timezone


from src.lib.responses import success

def health_check(event, context):
    return success({
        "status": "healthy",
        "stage": os.environ.get('STAGE'),
        "timestamp": datetime.now(timezone.utc).isoformat()

    })
