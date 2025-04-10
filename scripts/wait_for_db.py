import time
import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

def wait_for_db():
    while True:
        try:
            print(f"Attempting to connect to DB at {DATABASE_URL}...")
            conn = psycopg2.connect(DATABASE_URL)
            conn.close()
            print("Database is ready.")
            break
        except psycopg2.OperationalError as e:
            print(f"Error: {e}. Waiting for database...")
            time.sleep(5)  # Increase retry interval

if __name__ == "__main__":
    wait_for_db()