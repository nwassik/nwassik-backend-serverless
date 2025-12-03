"""Public module for application configuration."""

import json
import os

RUN_ENV = os.environ["RUN_ENV"]
STAGE = os.environ["STAGE"]

# running in cloud environment(ie deployed Lambda)
if RUN_ENV == "cloud":
    import boto3

    client = boto3.client(
        "secretsmanager",
        region_name=os.environ["AWS_REGION"],
    )
    # The secret here will be the one for the proper environment
    secret_value = client.get_secret_value(SecretId=os.environ["DATABASE_SECRET_NAME"])
    secret = json.loads(secret_value["SecretString"])

    os.environ["DATABASE_URL"] = secret["DATABASE_URL"]

elif RUN_ENV == "local":
    # running locally / tests
    from dotenv import load_dotenv

    load_dotenv()
else:
    exception_msg = f"RUN_ENV: {RUN_ENV} is not valid. It can only be 'cloud' or 'local'"
    raise ValueError(exception_msg)

BASE_DOMAIN = os.environ["BASE_DOMAIN"]
API_VERSION = os.environ["API_VERSION"]
DATABASE_URL = os.environ["DATABASE_URL"]
MAX_USER_CREATED_REQUESTS = os.environ["MAX_USER_CREATED_REQUESTS"]
MAX_USER_CREATED_FAVORITES = os.environ["MAX_USER_CREATED_FAVORITES"]
