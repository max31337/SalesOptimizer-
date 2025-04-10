import os  # Add this missing import
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import time

DB_URL = os.getenv("DATABASE_URL")
if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql+psycopg2://", 1) + "?sslmode=require"

engine = create_engine(DB_URL)
timeout = 30
start = time.time()

while True:
    try:
        with engine.connect() as conn:
            print("Database connection successful!")
            sys.exit(0)
    except OperationalError:
        print("Waiting for database...")
        if time.time() - start > timeout:
            print("Timeout waiting for database")
            sys.exit(1)
        time.sleep(2)