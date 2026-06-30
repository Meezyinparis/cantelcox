import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("COMMERCE_DB_HOST")
DB_PORT = int(os.getenv("COMMERCE_DB_PORT"))
DB_NAME = os.getenv("COMMERCE_DB_NAME")
DB_USER = os.getenv("COMMERCE_DB_USER")
DB_PASSWORD = os.getenv("COMMERCE_DB_PASSWORD")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_DB = int(os.getenv("REDIS_DB"))
