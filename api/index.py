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
    database = os.getenv("db_database")
    user = os.getenv("db_user")
    password = os.getenv("db_password")

    print("Tentando conectar à base de dados com os seguintes dados:")
    print(f"Host: {host}")
    print(f"Database: {database}")
    print(f"User: {user}")
    print(f"Password: {password}")

    connection = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )
    return connection

@app.route('/test-db')
def test_db_connection():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "success", "message": "Ligação à base de dados bem sucedida!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


