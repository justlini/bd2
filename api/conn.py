# conn.py
import psycopg2
import os

def get_db_connection():
    connection = psycopg2.connect(
        host=os.getenv("db_host"),
        database = os.getenv("db_database"),
        user= os.getenv("db_user"),
        password = os.getenv("db_password")
    )
    return connection
