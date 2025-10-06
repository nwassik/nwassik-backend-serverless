
from decimal import Decimal

from src.lib.responses import success, error
from src.lib.database import get_dynamodb_table_connexion

def list_requests(event, context):
    try:
        db = get_dynamodb_table_connexion()
        
        # TODO: Move from "scan" to "query"
        # scan is:
        #   Expensive - reads every item in table (you pay for all reads)
        #   Slow - has to check every single item
        #   Doesn't scale - gets slower as table grows
        response = db.scan(
            FilterExpression='begins_with(pk, :pk_prefix)',
            ExpressionAttributeValues={
                ':pk_prefix': 'REQUEST#'
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
            "total": len(requests)
        })
    # TODO: need to hide backend errors to the end user, or at least send a default "an error has occured", maybe identified with number
    except Exception as e:
        return error(str(e))