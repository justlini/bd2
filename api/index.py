import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

OK_CODE = 200
@app.route('/')
def hello_world():
    return 'Hello, World!'

def get_db_connection():
    host = os.getenv("db_host")
    connection = psycopg2.connect(
        host=host,
        database=os.getenv("db_database"),
        user=os.getenv("db_user"),
        password=os.getenv("db_password")
    )
    print(host)  #w Print host after it has been retrieved
    return connection

if __name__ == '__main__':
    app.run()
