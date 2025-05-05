import os
import psycopg2
from flask import Flask, jsonify, request  # Flask is now imported
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from api.conn import BaseDeDados
from utilizadores import Utilizadores
from quartos import ManageQuartos
from reservas import ManageReservas
from transacoes import ManageTransacoes
from bp_reservas import reservas_bp
import logging


# Configuração do Flask
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)
utilizadores = Utilizadores()
manageQuartos = ManageQuartos()
manageReservas = ManageReservas()
manageTransacoes = ManageTransacoes()
# Códigos HTTP
OK_CODE = 200
BAD_REQUEST = 400
CONFLICT = 409
INTERNAL_SERVER_ERROR = 500
CREATED = 201

bd = BaseDeDados()

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


app.register_blueprint(reservas_bp)

@app.route('/registar_emp', methods=['POST'])
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
@app.route('/registar_utilizador', methods=['POST'])
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
            # Login bem-sucedido
            user_data = {
                "idcliente": str(user[0]),
                "nome": str(user[1]),
                "email": str(user[2]),
                "tipo": str(user[4]) if user[4] else "cliente"  # Se não for admin, define como cliente
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

@app.route('/mudarPrecoQuarto', methods=['POST'])
@jwt_required()
def mudarprecoquarto():
    try:
        data = request.get_json()
        
        user = get_jwt_identity()
        
        if user['tipo'] != 'admin':
            logging.error("Unauthorized access attempt.")
            return jsonify({"error": "Unauthorized"}), BAD_REQUEST

        # Validar os parâmetros de entrada
        if not all(k in data for k in ["p_idquarto", "p_precoQuarto"]):
            logging.error("Faltam parametros!")
            return jsonify({"error": "Faltam parametros!"}), BAD_REQUEST

        # Chamar a função para mudar o preço do quarto
        message = manageQuartos.mudarPrecoQuarto(
            data['p_idquarto'],
            data['p_precoQuarto']
        )

        if "Preco do quarto alterado com sucesso!" in message:
            logging.info("Preco do quarto alterado com sucesso!")
            return jsonify({"message": message}), CREATED
        else:
            logging.error(f"Erro ao alterar preco do quarto: {message}")
            return jsonify({"error": message}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR

@app.route('/mudarTipoQuarto', methods=['POST'])
def mudartipoquarto():
    try:
        data = request.get_json()

        # Validar os parâmetros de entrada
        if not all(k in data for k in ["p_idquarto", "p_tipoquarto"]):
            logging.error("Faltam parametros!")
            return jsonify({"error": "Faltam parametros!"}), BAD_REQUEST

        # Chamar a função para mudar o tipo do quarto
        message = manageQuartos.mudarTipoQuarto(
            data['p_idquarto'],
            data['p_tipoquarto']
        )

        if "Tipo do quarto alterado com sucesso!" in message:
            logging.info("Tipo do quarto alterado com sucesso!")
            return jsonify({"message": message}), CREATED
        else:
            logging.error(f"Erro ao alterar tipo do quarto: {message}")
            return jsonify({"error": message}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR

@app.route('/get_ImagensQuarto', methods=['POST'])
def get_imagens_quarto():
    try:
        data = request.get_json()

        # Validar os parâmetros de entrada
        if not all(k in data for k in ["p_idquarto"]):
            logging.error("Faltam parametros!")
            return jsonify({"error": "Faltam parametros!"}), BAD_REQUEST

        # Chamar a função para obter as imagens do quarto
        imagens = manageQuartos.get_ImagensQuarto(
            data['p_idquarto']
        )

        if imagens:
            logging.info("Imagens do quarto obtidas com sucesso!")
            return jsonify({"imagens": imagens}), OK_CODE
        else:
            logging.error("Erro ao obter imagens do quarto.")
            return jsonify({"error": "Erro ao obter imagens do quarto."}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR

@app.route('/upload_imagem_quarto', methods=['POST'])
def upload_imagem_quarto_route():
    try:
        data = request.get_json()

        # Validar os parâmetros de entrada
        if not all(k in data for k in ["p_idquarto", "p_imagem"]):
            logging.error("Faltam parametros!")
            return jsonify({"error": "Faltam parametros!"}), BAD_REQUEST

        # Chamar a função para fazer o upload da imagem do quarto
        message = manageQuartos.upload_imagem_quarto(
            data['p_idquarto'],
            data['p_imagem']
        )

        if "Imagem do quarto carregada com sucesso!" in message:
            logging.info("Imagem do quarto carregada com sucesso!")
            return jsonify({"message": message}), CREATED
        else:
            logging.error(f"Erro ao carregar imagem do quarto: {message}")
            return jsonify({"error": message}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR

@app.route('/ver_disponibilidade_quarto', methods=['GET'])
def ver_disponibilidade_quarto_route():
    try:
        disponibilidade = manageQuartos.ver_disponibilidade_quarto()
        return jsonify({"disponibilidade": disponibilidade}), OK_CODE
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR
    
    

    
@app.route('/cancelar_reserva', methods=['POST'])
@jwt_required()
def cancelar_reserva():
    try:
        data = request.get_json()
        
        user = get_jwt_identity()
        
        if user['tipo'] not in ['admin', 'rececionista']:
            logging.error("Unauthorized access attempt.")
            return jsonify({"error": "Unauthorized"}), BAD_REQUEST

        # Validar os parâmetros de entrada
        if not all(k in data for k in ["p_idreserva"]):
            logging.error("Faltam parametros!")
            return jsonify({"error": "Faltam parametros!"}), BAD_REQUEST

        # Chamar a função para pagar a reserva
        message = manageReservas.cancelar_reserva(
            data['p_idreserva']
        )

        if "Reserva paga com sucesso!" in message:
            logging.info("Reserva paga com sucesso!")
            return jsonify({"message": message}), CREATED
        else:
            logging.error(f"Erro ao pagar reserva: {message}")
            return jsonify({"error": message}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR

@app.route('/ver_reservasCliente', methods=['POST'])
@jwt_required()
def ver_reservas_cliente():
    try:
        data = request.get_json()
        
        user = get_jwt_identity()
        
        if user['tipo'] not in ['admin', 'rececionista', 'cliente']:
            logging.error("Unauthorized access attempt.")
            return jsonify({"error": "Unauthorized"}), BAD_REQUEST
        
        if user['tipo'] == 'cliente' and data['p_idcliente'] != user['idcliente']:
            logging.error("Unauthorized access attempt.")
            return jsonify({"error": "Unauthorized"}), BAD_REQUEST


        # Validar os parâmetros de entrada
        if not all(k in data for k in ["p_idcliente"]):
            logging.error("Faltam parametros!")
            return jsonify({"error": "Faltam parametros!"}), BAD_REQUEST

        # Chamar a função para ver as reservas do cliente
        reservas = manageReservas.ver_reservasCliente(
            data['p_idcliente']
        )

        if reservas:
            logging.info("Reservas do cliente obtidas com sucesso!")
            return jsonify({"reservas": reservas}), OK_CODE
        else:
            logging.error("Erro ao obter reservas do cliente.")
            return jsonify({"error": "Erro ao obter reservas do cliente."}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR
    
@app.route('/ver_todasReservas', methods=['POST'])
@jwt_required()
def ver_todas_reservas():
    try:
        user = get_jwt_identity()
        
        if user['tipo'] not in ['admin']:
            logging.error("Unauthorized access attempt.")
            return jsonify({"error": "Unauthorized"}), BAD_REQUEST

        # Chamar a função para ver todas as reservas
        reservas = manageReservas.ver_todasReservas()

        if reservas:
            logging.info("Todas as reservas obtidas com sucesso!")
            return jsonify({"reservas": reservas}), OK_CODE
        else:
            logging.error("Erro ao obter todas as reservas.")
            return jsonify({"error": "Erro ao obter todas as reservas."}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR
    
    
@app.route('/ver_pagamentos', methods=['POST'])
@jwt_required()
def ver_pagamentos():
    try:
        user = get_jwt_identity()
        
        if user['tipo'] not in ['admin']:
            logging.error("Unauthorized access attempt.")
            return jsonify({"error": "Unauthorized"}), BAD_REQUEST
        
        # Chamar a função para ver todos os pagamentos
        pagamentos = manageTransacoes.ver_pagamentos()

        if pagamentos:
            logging.info("Todos os pagamentos obtidos com sucesso!")
            return jsonify({"pagamentos": pagamentos}), OK_CODE
        else:
            logging.error("Erro ao obter todos os upagamentos.")
            logging.error("Erro ao obter todos os pagamentos.")
            # erro no postman
            return jsonify({"error": "Erro ao obter todos os pagamentos."}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR
    
@app.route('/ver_pagamentos_cliente', methods=['POST'])
@jwt_required()
def ver_pagamentos_cliente():
    try:
        data = request.get_json()
        
        user = get_jwt_identity()
        
        if user['tipo'] not in ['admin', 'cliente']:
            logging.error("Unauthorized access attempt.")
            return jsonify({"error": "Unauthorized"}), BAD_REQUEST
        
        if user['tipo'] == 'cliente' and data['p_idcliente'] != user['idcliente']:
            logging.error("Unauthorized access attempt.")
            return jsonify({"error": "Unauthorized"}), BAD_REQUEST

        # Validar os parâmetros de entrada
        if not all(k in data for k in ["p_idcliente"]):
            logging.error("Faltam parametros!")
            return jsonify({"error": "Faltam parametros!"}), BAD_REQUEST

        # Chamar a função para ver os pagamentos do cliente
        pagamentos = manageTransacoes.verpagamentos_cliente(
            data['p_idcliente']
        )

        if pagamentos:
            logging.info("Pagamentos do cliente obtidos com sucesso!")
            return jsonify({"pagamentos": pagamentos}), OK_CODE
        else:
            logging.error("Erro ao obter pagamentos do cliente.")
            return jsonify({"error": "Erro ao obter pagamentos do cliente."}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR

# Execução do aplicativo Flask
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
