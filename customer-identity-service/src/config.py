import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("IDENTITY_DB_HOST")
DB_PORT = int(os.getenv("IDENTITY_DB_PORT"))
DB_NAME = os.getenv("IDENTITY_DB_NAME")
DB_USER = os.getenv("IDENTITY_DB_USER")
DB_PASSWORD = os.getenv("IDENTITY_DB_PASSWORD")