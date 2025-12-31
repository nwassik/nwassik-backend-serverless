import json
from uuid import uuid4
from src.handlers.requests.create import create_request
from src.handlers.requests.get import get_request

# ------------------------------------------------------------
# # Example body for a buy_and_deliver request
# body = {
#     "type": "buy_and_deliver",
#     "title": "Buy ffffff",
#     "description": "Need a package delivered from France",
#     "dropoff_latitude": 36.8,
#     "dropoff_longitude": 10.2,
# }

# # Mock Lambda event
# event = {
#     "body": json.dumps(body),
#     "requestContext": {
#         "authorizer": {
#             "claims": {
#                 "sub": str(uuid4())  # user_id for testing
#             }
#         }
#     },
# }

# print(event["requestContext"]["authorizer"]["claims"]["sub"])
# # Context can be None for local testing
# response = create_request(event, None)

# ------------------------------------------------------------
### GET EVENT
test_event = {
    "pathParameters": {"request_id": "71304aaf-b679-476e-882a-7789fcd9a839"},
    "requestContext": {
        "authorizer": {"claims": {"sub": "8dcaf6c9-2cd3-4185-997d-032e61197d49"}}
    },
}
response = get_request(test_event, None)

# ------------------------------------------------------------
print(response)
