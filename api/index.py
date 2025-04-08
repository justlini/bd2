import os
import psycopg2
from flask import Flask, jsonify, request  
import logging

# Configuração do Flask
app = Flask(__name__)

# Códigos HTTP
OK_CODE = 200
BAD_REQUEST = 400
CONFLICT = 409
INTERNAL_SERVER_ERROR = 500
CREATED = 201

# Rota de teste
@app.route('/')
def hello_world():
    return 'Hello, World!'

# caminho para ir buscar as variaveis de ambiente
@app.route('/env')
def print_env_vars():
    env_vars = {
        "db_host": os.getenv("db_host"),
        "db_database": os.getenv("db_database"),
        "db_user": os.getenv("db_user"),
        "db_password": os.getenv("db_password")
    }
    return jsonify(env_vars), OK_CODE

# Função para conectar na base de dados
def get_db_connection():
    # buscar as variaveis de ambiente
    host = os.getenv("db_host")
    database = os.getenv("db_database")
    user = os.getenv("db_user")
    password = os.getenv("db_password")

    # Verifica se todas as variáveis de ambiente existem
    if not all([host , database, user, password]):
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

def insert_user(nome, email, nif, senha, numerotelefone):
    conn = get_db_connection()
    #se a conexaõ for None retorna um erro de conexão
    if conn is None:
        return "Erro de conexão com a base de dados."
    
    try:
        cur = conn.cursor()
        #procidure inserir_utilizadores
        cur.execute("CALL inserir_utilizadores(%s, %s, %s, %s, %s);", (nome, email, nif, senha, numerotelefone))
        conn.commit()
        cur.close()
        conn.close()
        return "Utilizador inserido com sucesso!"
    except Exception as e:
        return str(e)

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
        return "Empregado inserirdo com sucesso!"
    except Exception as e:
        return str(e)


def insert_quarto(p_numeroquarto, p_precoquarto, p_tipoquarto):
    conn = get_db_connection()
    if conn is None:
        return "Erro de conexão com a base de dados."

    try:
        cur = conn.cursor()
        # Correct the query to pass all parameters dynamically
        cur.execute("CALL inserir_quartos(%s, %s, %s);", (p_numeroquarto, p_precoquarto, p_tipoquarto))
        conn.commit()
        cur.close()
        conn.close()
        return "Quarto inserido com sucesso!"
    except Exception as e:
        return str(e)

@app.route('/inserir_emp', methods=['POST'])
def register_emp():
    try:
        data = request.get_json()
        #debug de erros descomentar quando estiver a dar treta
        #logging.debug(f"Received data: {data}")

        #verificar se todos os parametros existem
        if not all(k in data for k in ["idemp", "tipoemp", "idcliente"]):
            logging.error("Faltam parametros!")

            #erro no postman
            return jsonify({"error": "Faltam parametros!"}), BAD_REQUEST

        #verificar se o empregado já exsite
        if emp_exists(data["idemp"], data["idcliente"]):
            logging.error("Empregado com este ID já existe")
            logging.error("Utilizador com este mail ou NIF já existe!")

            # erro no postman
            return jsonify({"error": "Utilizador com este mail ou NIF já existe!"}), CONFLICT

        #verificar se o tipo de empregado é admin ou rececionista
        if data["tipoemp"] not in ["admin", "rececionista"]:
            logging.error("Tipo de mepregado invalido!")

            # erro no postman
            return jsonify({"error": "Tipo de mepregado invalido!"}), BAD_REQUEST

        #formato do body json esperado
        message = insert_emp(
            data['idemp'], 
            data['tipoemp'], 
            data['idcliente']
        )

        #empregado existe
        if "Empregado inserido com sucesso!" in message:
            logging.info("Empregado inserido com sucesso!")

            #mensagem sucess no postman
            return jsonify({"message": message}), CREATED
        else:
            logging.error(f"Erro ao inserir empregado: {message}")
            return jsonify({"error": message}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR
    
@app.route('/inserir_quarto', methods=['POST'])
def registar_quarto():
    try:
        data = request.get_json()

        # Validate input parameters
        if not all(k in data for k in ["p_numeroquarto", "p_precoquarto", "p_tipoquarto"]):
            logging.error("Faltam parametros!")
            return jsonify({"error": "Faltam parametros!"}), BAD_REQUEST

        # Check if the room already exists
        if quarto_exists(data["p_numeroquarto"]):
            logging.error("Quarto com esse numero já existe!")
            return jsonify({"error": "Quarto com esse numero já existe!"}), CONFLICT

        # Validate room type
        if data["p_tipoquarto"] not in ["casal", "solteiro"]:
            logging.error("Tipo de quarto invalido!")
            return jsonify({"error": "Tipo de quarto invalido!"}), BAD_REQUEST

        # Call the insert_quarto function
        message = insert_quarto(
            data['p_numeroquarto'],
            data['p_precoquarto'],
            data['p_tipoquarto']
        )

        if "Quarto inserido com sucesso!" in message:
            logging.info("Quarto inserido com sucesso!")
            return jsonify({"message": message}), CREATED
        else:
            logging.error(f"Erro ao inserir quarto: {message}")
            return jsonify({"error": message}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR

# Função para verificar se o empregado já existe
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
        return result is not None  # Retorna True se o utilizador existir
    except Exception as e:
        return False  # Retorna False caso haja erro na execução da consulta

# Função para verificar se o utilizador já existe
def user_exists(email, nif):
    conn = get_db_connection()
    if conn is None:
        return False  # Se não conseguir se conectar na base de dados, assume que o utilizador não existe
    
    try:
        cur = conn.cursor()
        query = "SELECT 1 FROM public.utilizadores WHERE email = %s OR nif = %s LIMIT 1"
        cur.execute(query, (email, nif))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result is not None  # Retorna True se o utilizador existir
    except Exception as e:
        return False  # Retorna False caso haja erro na execução da consultaº

# Função para verificar se o quarto já existe
def quarto_exists(p_numeroquarto):
    conn = get_db_connection()
    if conn is None:
        return False  # Se não conseguir se conectar na base de dados, assume que o utilizador não existe

    try:
        cur = conn.cursor()
        query = "SELECT 1 FROM public.quartos WHERE p_numeroquarto = %s LIMIT 1"
        cur.execute(query, (p_numeroquarto))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result is not None  # Retorna True se o quarto existir
    except Exception as e:
        return False  # Retorna False caso haja erro na execução da consulta

# Caminho para registrar um novo utilziador
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
