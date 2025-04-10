import time
import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

def wait_for_db():
    retries = 0
    max_retries = 30

    while retries < max_retries:
        try:
            print(f"[wait_for_db] Attempting to connect to DB at {DATABASE_URL}...")
            conn = psycopg2.connect(DATABASE_URL)
            conn.close()
            print("[wait_for_db] SUCCESS: Connected to the database!")
            return
        except psycopg2.OperationalError as e:
            print(f"[wait_for_db] Attempt {retries + 1}: Database not ready. Error: {e}")
            retries += 1
            time.sleep(3)
    
    print("[wait_for_db] ERROR: Could not connect to the database after multiple attempts.")
    exit(1)

if __name__ == "__main__":
    wait_for_db()