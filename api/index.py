import os
import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

OK_CODE = 200

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/env')
def print_env_vars():
    env_vars = {
        "db_host": os.getenv("db_host"),
        "db_database": os.getenv("db_database"),
        "db_user": os.getenv("db_user"),
        "db_password": os.getenv("db_password")
    }
    return jsonify(env_vars), OK_CODE

def get_db_connection():
    host = os.getenv("db_host")
    connection = psycopg2.connect(
        host=host,
        database=os.getenv("db_database"),
        user=os.getenv("db_user"),
        password=os.getenv("db_password")
    )
    print(f"Connected to DB at host: {host}")
    return connection

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

