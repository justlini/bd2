import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

OK_CODE = 200
@app.route('/')
def hello_world():
    return 'LUME!'

def db_connection():
    credentials = "host= aid.estgoh.ipc.pt dbname=db20221090306 port=5432 user=a2022109306  password=a2022109306"
    return psycopg2.connect(credentials)

if __name__ == '__main__':
    app.run()