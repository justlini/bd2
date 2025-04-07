import os
import psycopg2
from flask import Flask, jsonify,request

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


def insert_user(nome, email, nif, senha, numerotelefone):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Use CALL to call the stored procedure in PostgreSQL
        cur.execute("""
            CALL inserir_utilizadores(%s, %s, %s, %s, %s);
        """, (nome, email, nif, senha, numerotelefone))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return True, "User inserted successfully!"
    except Exception as e:
        return False, str(e)

def user_exists(email, nif):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        query = "SELECT 1 FROM public.utilizadores WHERE email = %s OR nif = %s LIMIT 1"
        cur.execute(query, (email, nif))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result is not None
    except Exception as e:
        return False

@app.route("/register", methods=['POST'])
def register():
    data = request.get_json()

    # Check if all required fields are present
    if "nome" not in data or "email" not in data or "nif" not in data or "senha" not in data or "numerotelefone" not in data:
        return jsonify({"error": "Missing required parameters"}),

    # Check if user already exists
    if user_exists(data["email"], data["nif"]):
        return jsonify({"error": "User with this email or NIF already exists"}), 

    # Insert user into database
    #insert
    success, message = insert_user(
        data['nome'], 
        data['email'], 
        data['nif'], 
        data['senha'], 
        data['numerotelefone']
    )

    if success:
        return jsonify({"message": message}), 
    else:
        return jsonify({"error": message}),


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')