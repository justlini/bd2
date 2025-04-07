# conn.py
import psycopg2
import os


def get_db_connection():
    host = os.getenv("db_host")
    connection = psycopg2.connect(
        host=host,
        database=os.getenv("db_database"),
        user=os.getenv("db_user"),
        password=os.getenv("db_password")
    )
    print(host)  # Print host after it has been retrieved
    return connection
