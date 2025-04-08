import os
import psycopg2
from flask import Flask, jsonify, request  
import logging

# Configuração do Flask
app = Flask(__name__)

# Códigos HTTP de resposta
OK_CODE = 200
BAD_REQUEST = 400
CONFLICT = 409
INTERNAL_SERVER_ERROR = 500
CREATED = 201

# Rota de teste
@app.route('/')
def hello_world():
    return 'Hello, World!'

# Rota para verificar variáveis de ambiente
@app.route('/env')
def print_env_vars():
    env_vars = {
        "db_host": os.getenv("db_host"),
        "db_database": os.getenv("db_database"),
        "db_user": os.getenv("db_user"),
        "db_password": os.getenv("db_password")
    }
    return jsonify(env_vars), OK_CODE

# Função para conectar ao banco de dados
def get_db_connection():
    # Obtém as variáveis de ambiente
    host = os.getenv("db_host")
    database = os.getenv("db_database")
    user = os.getenv("db_user")
    password = os.getenv("db_password")

    # Verifica se todas as variáveis de ambiente estão presentes
    if not all([host, database, user, password]):
        return None  # Retorna None se faltar alguma variável

    try:
        # Conecta à base de dados
        connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        return connection  # Retorna a conexão
    except Exception as e:
        print(f"Erro ao ciionectar à base de dados: {str(e)}")
        return None

# Função para inserir um usuário no banco de dados
def insert_user(nome, email, nif, senha, numerotelefone):
    conn = get_db_connection()
    if conn is None:
        return "Erro de conexão com a base de dados."
    
    try:
        cur = conn.cursor()
        cur.execute("CALL inserir_utilizadores(%s, %s, %s, %s, %s);", (nome, email, nif, senha, numerotelefone))
        conn.commit()
        cur.close()
        conn.close()
        return "User inserted successfully!"  # Retorna a mensagem de sucesso
    except Exception as e:
        return str(e)  # Retorna o erro ocorrido

def insert_emp(idemp, tipoemp, idcliente):
    conn = get_db_connection()
    if conn is None:
        return "Erro de conexão com a base de dados."

    try:
        cur = conn.cursor()
        cur.execute("CALL inserir_emp(%s, %s, %s);", (idemp, tipoemp, idcliente))
        conn.commit()
        cur.close()
        conn.close()
        return "empregado inserirdo com sucesso"
    except Exception as e:
        return str(e)
    
@app.route('/inserir_emp', methods=['POST'])
def register_emp():
    try:
        data = request.get_json()

        logging.debug(f"Received data: {data}")

        if not all(k in data for k in ["idemp", "tipoemp", "idcliente"]):
            logging.error("Missing required parameters.")
            return jsonify({"error": "Missing required parameters"}), BAD_REQUEST

        if emp_exists(data["idemp"], data["idcliente"]):
            logging.error("Employee with this ID or client already exists.")
            logging.error("User with this email or NIF already exists.")
            return jsonify({"error": "User with this email or NIF already exists"}), CONFLICT
        
        if data["tipoemp"] not in ["admin", "rececionista"]:
            logging.error("Invalid employee type.")
            return jsonify({"error": "Invalid employee type"}), BAD_REQUEST

        message = insert_emp(
            data['idemp'], 
            data['tipoemp'], 
            data['idemp']
        )

        if "Employee inserted successfully!" in message:
            logging.info("Empolye inserted successfully.")
            return jsonify({"message": message}), CREATED
        else:
            logging.error(f"Error inserting employee: {message}")
            return jsonify({"error": message}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR
    
def emp_exists(idemp, idcliente):
    conn = get_db_connection()
    if conn is None:
        return False  # Se não conseguir se conectar ao banco, assume que o usuário não existe
    
    try:
        cur = conn.cursor()
        query = "SELECT 1 FROM public.emp WHERE idemp = %s OR idcliente = %s LIMIT 1"
        cur.execute(query, (idemp, idcliente))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result is not None  # Retorna True se o usuário existir
    except Exception as e:
        return False  # Retorna False caso haja erro na execução da consulta

# Função para verificar se o usuário já existe
def user_exists(email, nif):
    conn = get_db_connection()
    if conn is None:
        return False  # Se não conseguir se conectar ao banco, assume que o usuário não existe
    
    try:
        cur = conn.cursor()
        query = "SELECT 1 FROM public.utilizadores WHERE email = %s OR nif = %s LIMIT 1"
        cur.execute(query, (email, nif))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result is not None  # Retorna True se o usuário existir
    except Exception as e:
        return False  # Retorna False caso haja erro na execução da consulta

# Rota para registrar um novo usuário
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        logging.debug(f"Received data: {data}")

        if not all(k in data for k in ["nome", "email", "nif", "senha", "numerotelefone"]):
            logging.error("Missing required parameters.")
            return jsonify({"error": "Missing required parameters"}), BAD_REQUEST

        if user_exists(data["email"], data["nif"]):
            logging.error("User with this email or NIF already exists.")
            return jsonify({"error": "User with this email or NIF already exists"}), CONFLICT

        message = insert_user(
            data['nome'], 
            data['email'], 
            data['nif'], 
            data['senha'], 
            data['numerotelefone']
        )

        if "User inserted successfully!" in message:
            logging.info("User inserted successfully.")
            return jsonify({"message": message}), CREATED
        else:
            logging.error(f"Error inserting user: {message}")
            return jsonify({"error": message}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR

# Rota para login de usuário
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        # Log dos dados recebidos
        logging.debug(f"Login data received: {data}")

        # Verifica se email e senha estão presentes
        if not all(k in data for k in ["email", "senha"]):
            logging.error("Missing email or password.")
            return jsonify({"error": "Missing email or password"}), BAD_REQUEST

        # Conexão com o banco
        conn = get_db_connection()
        if conn is None:
            logging.error("Database connection failed.")
            return jsonify({"error": "Database connection failed"}), INTERNAL_SERVER_ERROR

        cur = conn.cursor()
        query = "SELECT idcliente, nome, email FROM public.utilizadores WHERE email = %s AND senha = %s"
        cur.execute(query, (data["email"], data["senha"]))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            # Login bem-sucedido
            user_data = {
                "idcliente": user[0],
                "nome": user[1],
                "email": user[2]
            }
            logging.info(f"User {user[2]} logged in successfully.")
            return jsonify({"message": "Login successful", "user": user_data}), OK_CODE
        else:
            logging.warning("Invalid email or password.")
            return jsonify({"error": "Invalid email or password"}), BAD_REQUEST
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR


# Execução do aplicativo Flask
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
