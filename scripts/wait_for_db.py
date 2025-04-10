import time
import psycopg2
import os
from urllib.parse import urlparse

def wait_for_db():
    max_retries = 30  # Maximum number of retries (5 seconds each = 2.5 minutes total)
    retries = 0
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Handle Railway's postgres:// format
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    while retries < max_retries:
        try:
            print(f"Attempting to connect to database (attempt {retries + 1}/{max_retries})...")
            # Hide sensitive information in logs
            parsed_url = urlparse(DATABASE_URL)
            safe_url = f"postgresql://{parsed_url.hostname}:{parsed_url.port}/{parsed_url.path.lstrip('/')}"
            print(f"Connection URL (sanitized): {safe_url}")
            
            conn = psycopg2.connect(DATABASE_URL)
            conn.close()
            print("✅ Database is ready!")
            return True
        except psycopg2.OperationalError as e:
            retries += 1
            print(f"⚠️ Database connection failed: {str(e).split('\\n')[0]}")
            if retries < max_retries:
                print(f"Retrying in 5 seconds... ({retries}/{max_retries})")
                time.sleep(5)
            else:
                print("❌ Maximum retries reached. Database connection failed.")
                return False

if __name__ == "__main__":
    if not wait_for_db():
        exit(1)  # Exit with error code if database connection fails