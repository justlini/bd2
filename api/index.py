import os
import psycopg2
from flask import Flask, jsonify, request  
import logging  


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

@app.route('/ola')
def get_db_connection():
    # Obtém as variáveis de ambiente
    host = os.getenv("db_host")
    database = os.getenv("db_database")
    user = os.getenv("db_user")
    password = os.getenv("db_password")

    # Verifica se todas as variáveis de ambiente estão presentes
    if not all([host, database, user, password]):
        return jsonify({"error": "Missing environment variables"}), 400

    print("Tentando conectar à base de dados com os seguintes dados:")
    print(f"Host: {host}")
    print(f"Database: {database}")
    print(f"User: {user}")
    print(f"Password: {password}")

    try:
        # Conecta à base de dados
        connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        # Se a conexão for bem-sucedida
        connection.close()  # Fecha a conexão após a tentativa
        return jsonify({"message": "Conexão bem-sucedida com a base de dados!"}), 200
    except Exception as e:
        # Se ocorrer um erro na conexão
        return jsonify({"error": f"Erro ao conectar à base de dados: {str(e)}"}), 500

def insert_user(nome, email, nif, senha, numerotelefone):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("CALL inserir_utilizadores(%s, %s, %s, %s, %s);", (nome, email, nif, senha, numerotelefone))
        conn.commit()
        cur.close()
        conn.close()
        return "User inserted successfully!"
    except Exception as e:
        return str(e)

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

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not all(k in data for k in ["nome", "email", "nif", "senha", "numerotelefone"]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    if user_exists(data["email"], data["nif"]):
        return jsonify({"error": "User already exists"}), 409

    message = insert_user(data['nome'], data['email'], data['nif'], data['senha'], data['numerotelefone'])
    if "successfully" in message:
        return jsonify({"message": message}), 201
    else:
        return jsonify({"error": message}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
