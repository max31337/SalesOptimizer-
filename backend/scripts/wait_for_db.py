import time, psycopg2, os

while True:
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        conn.close()
        break
    except Exception as e:
        print("DB not ready, waiting...", e)
        time.sleep(2)