import os
import psycopg
from datetime import datetime

DB_TIMEZONE = datetime.now().astimezone().tzinfo
print(f"Using timezone: {DB_TIMEZONE}")


def get_db_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "monitoring"),
        dbname=os.getenv("POSTGRES_DB", "course_assistant"),
        user=os.getenv("POSTGRES_USER", "user"),
        password=os.getenv("POSTGRES_PASSWORD", "pswd"),
    )
