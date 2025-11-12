import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
MAX_USER_CREATED_REQUESTS = os.environ["MAX_USER_CREATED_REQUESTS"]
MAX_USER_CREATED_FAVORITES = os.environ["MAX_USER_CREATED_FAVORITES"]
