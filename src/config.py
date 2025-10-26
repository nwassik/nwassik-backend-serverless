import os

from dotenv import load_dotenv

load_dotenv()

# TODO: Prefix environments with APP_LEVEl and RUNTIME_LEVEL depending on where they are needed or
# maybe put them in two different objects of these typese

DATABASE_URL = os.environ["DATABASE_URL"]
MAX_USER_CREATED_REQUESTS = 20
MAX_USER_CREATED_FAVORITES = 100
