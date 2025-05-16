from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from api.conn import BaseDeDados
import logging
from utilizadores import Utilizadores
import bcrypt
import os
from auditoria import ManageAuditoria
from datetime import datetime

OK_CODE = 200
BAD_REQUEST = 400
CONFLICT = 409
INTERNAL_SERVER_ERROR = 500
CREATED = 201

utilizadores_bp = Blueprint('utilizadores', __name__)

utilizadores = Utilizadores()
manageAuditoria = ManageAuditoria()

bd = BaseDeDados()

@utilizadores_bp.route('/registar_emp', methods=['POST'])
@jwt_required()
def registar_emp():
    try:
        user = get_jwt_identity()
        data = request.get_json()
        p_dataLog= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        p_utilizador_app = user['nome']
        p_utilizador_bd = user['db_user']
        p_dataLog = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        #debug de erros descomentar quando estiver a dar treta
        #logging.debug(f"Received data: {data}")

        #verificar se todos os parametros existem
        if not all(k in data for k in ["idemp", "tipoemp", "idcliente"]):
            logging.error("Faltam parametros!")

            #erro no postman
            return jsonify({"error": "Faltam parametros!"}), BAD_REQUEST
        
        if user['tipo'] not in ['admin']:
            logging.error("Tentativa de acesso não autorizado.")
            return jsonify({"error": "Nao autorizado"}), BAD_REQUEST

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
            return jsonify({"error": "Tipo de empregado invalido!"}), BAD_REQUEST

        #formato do body json esperado
        message = utilizadores.insert_emp(
            data['idemp'],
            data['tipoemp'],
            data['idcliente']
        )
        
        #empregado existe
        if "Empregado inserido com sucesso!" in message:
            logging.info("Empregado inserido com sucesso!")
            log_message = f"Conta empregado criada: {data['idemp']}"
            manageAuditoria.insert_Log(p_utilizador_bd,p_utilizador_app,p_dataLog,log_message)

            #mensagem sucess no postman
            return jsonify({"utilizador inserido": message}), CREATED
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
        p_dataLog = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logging.debug(f"Received data: {data}")
        

        if not all(k in data for k in ["nome", "email", "nif", "senha", "numerotelefone"]):
            logging.error("Missing required parameters.")
            return jsonify({"error": "Missing required parameters"}), BAD_REQUEST

        if utilizadores.user_exists(data["email"], data["nif"]):
            logging.error("Utilizador com este email ou NIF já existe!")
            return jsonify({"error": "Utilizador com este email ou NIF já existe"}), CONFLICT
        
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
            log_message = f"Conta criada: {data['email']}"
            message = manageAuditoria.insert_Log(data['nome'],data['email'],p_dataLog,log_message)
            return jsonify({"message": message}), CREATED
        else:
            logging.error(f"Erro ao inserir utilizador: {message}")
            return jsonify({"error": message}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR
    

@utilizadores_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        # Dados recebidos
        logging.debug(f"Dados login recebidos: {data}")

        # Validar os parâmetros de entrada
        if not all(k in data for k in ["email", "senha"]):
            logging.error("Faltam parametros!")
            return jsonify({"error": "Faltam parametros"}), BAD_REQUEST

        conn = bd.get_conn()
        if conn is None:
            logging.error("Conexão a base de dados falhou.")
            return jsonify({"error": "Conexao a base de dados falhou"}), INTERNAL_SERVER_ERROR

        cur = conn.cursor()
        cur.execute("SELECT * FROM public.get_userData(%s)", (data["email"],))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and bcrypt.checkpw(data['senha'].encode('utf-8'), user[3].encode('utf-8')):
            # Se a senha estiver correta, verificar o tipo de utilizador
            # user[4] é o tipo de utilizador (admin, rececionista, cliente) se for none é um cliente
            role = str(user[4]) if user[4] else "cliente"

            # Fazer a conexão à base de dados com o tipo de utilizadoR
            conn_nova = BaseDeDados(user_type=role)
            if conn_nova.get_conn() is None:
                logging.error("Conexão a base de dados falhou.")
                return jsonify({"error": "Conexao a base de dados falhou"}), INTERNAL_SERVER_ERROR

            # Criar o token de acesso
            user_data = {
                "idcliente": str(user[0]),
                "nome": str(user[1]),
                "email": str(user[2]),
                "tipo": role,  # Store the role
                "db_user": conn_nova.user
            }
            token = create_access_token(identity=user_data)
        

            logging.info(f"Utilizador {user[2]} logou com sucesso com o {role}.")
            return jsonify({"message": "Login com sucesso", "access_token": token, "user": user_data}), OK_CODE
        else:
            logging.warning("Email invalido ou password.")
            return jsonify({"error": "Email invalido ou password"}), BAD_REQUEST
    except Exception as e:
        logging.error(f"Erro login: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR