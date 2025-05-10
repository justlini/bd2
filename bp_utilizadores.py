from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from api.conn import BaseDeDados
import logging
from utilizadores import Utilizadores
import bcrypt
import os

OK_CODE = 200
BAD_REQUEST = 400
CONFLICT = 409
INTERNAL_SERVER_ERROR = 500
CREATED = 201

utilizadores_bp = Blueprint('utilizadores', __name__)

utilizadores = Utilizadores()


bd = BaseDeDados()

@utilizadores_bp.route('/registar_emp', methods=['POST'])
def registar_emp():
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
        if utilizadores.emp_exists(data["idemp"], data["idcliente"]):
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
        message = utilizadores.insert_emp(
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
    


# Caminho para registrar um novo utilziador
@utilizadores_bp.route('/registar_utilizador', methods=['POST'])
def register():
    try:
        data = request.get_json()

        logging.debug(f"Received data: {data}")
        

        if not all(k in data for k in ["nome", "email", "nif", "senha", "numerotelefone"]):
            logging.error("Missing required parameters.")
            return jsonify({"error": "Missing required parameters"}), BAD_REQUEST

        if utilizadores.user_exists(data["email"], data["nif"]):
            logging.error("User with this email or NIF already exists.")
            logging.error("Empregado com este ID já existe")
            logging.error("Utilizador com este mail ou NIF já existe!")
            return jsonify({"error": "User with this email or NIF already exists"}), CONFLICT
        
        hashar_password = bcrypt.hashpw(data['senha'].encode('utf-8'), bcrypt.gensalt())
    

        message = utilizadores.insert_user(
            data['nome'], 
            data['email'], 
            data['nif'], 
            #data['senha'],
            hashar_password.decode('utf-8'), # Descomentar se quiser usar a senha hasheada
            data['numerotelefone']
        )

        if "Utilizador inserido com sucesso!" in message:
            logging.info("Utilizador inserido com sucesso!")
            return jsonify({"message": message}), CREATED
        else:
            logging.error(f"Error inserting user: {message}")
            return jsonify({"error": message}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR
    

@utilizadores_bp.route('/login', methods=['POST'])
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
        conn = bd.get_conn()
        if conn is None:
            logging.error("Database connection failed.")
            return jsonify({"error": "Database connection failed"}), INTERNAL_SERVER_ERROR

        cur = conn.cursor()
        cur.execute("Select * from public.get_userData(%s)", (data["email"],))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and bcrypt.checkpw(data['senha'].encode('utf-8'), user[3].encode('utf-8')):
        
            role = str(user[4]) if user[4] else "cliente"
            role_user = os.getenv(f"{role}_db_user")
            role_password = os.getenv("db_password")
            conn_nova = BaseDeDados(user=role_user, password=role_password)
            if conn_nova.get_conn() is None:
                logging.error("Database connection failed.")
                return jsonify({"error": "Database connection failed"}), INTERNAL_SERVER_ERROR

            # Login bem-sucedido
            user_data = {
                "idcliente": str(user[0]),
                "nome": str(user[1]),
                "email": str(user[2]),
                "tipo": role_user # Se não for admin, define como cliente
            }
            token = create_access_token(identity=user_data)
            logging.info(f"User {user[2]} logged in successfully.")
            return jsonify({"message": "Login successful", "access_token": token, "user": user_data}), OK_CODE
        else:
            logging.warning("Invalid email or password.")
            return jsonify({"error": "Invalid email or password"}), BAD_REQUEST
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR