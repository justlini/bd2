from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from api.conn import BaseDeDados
import logging
from reservas import ManageReservas
from auditoria import ManageAuditoria

OK_CODE = 200
BAD_REQUEST = 400
CONFLICT = 409
INTERNAL_SERVER_ERROR = 500
CREATED = 201


# Create the Blueprint
reservas_bp = Blueprint('reservas', __name__)

manageReservas = ManageReservas()
manageAuditoria = ManageAuditoria()
p_utilizador_bd = "teste"
p_utilizador_app = "teste"

@reservas_bp.route('/pagar_reserva/<int:id_reserva>', methods=['POST'])
@jwt_required()
def pagar_reserva(id_reserva):
    try:
        # Obter os dados do utilizador autenticado
        user = get_jwt_identity()
        p_utilizador_app = user['nome']
        p_utilizador_bd = user['db_user']
        p_dataLog= datetime.now()
        
        if user['tipo'] not in ['admin', 'rececionista']:
            logging.error("Unauthorized access attempt.")
            return jsonify({"error": "Unauthorized"}), 400 
        message = manageReservas.pagar_reserva(id_reserva)

        log_message = f"Pagar reserva: {id_reserva}"

        message = manageAuditoria.insert_Log(p_utilizador_bd,p_utilizador_app,p_dataLog,log_message)

        if "Reserva paga com sucesso!" in message:
            logging.info("Reserva paga com sucesso!")
            return jsonify({"message": message}), 201  
        else:
            logging.error(f"Erro ao pagar reserva: {message}")
            return jsonify({"error": message}), 500 
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
    
@reservas_bp.route('/reserva/<int:id_cliente>/<int:id_quarto>/inserir', methods=['POST'])
def registar_reserva(id_cliente, id_quarto):
    try:
        data = request.get_json()

        # validar os parametros de entrada
        if not all(k in data for k in ["p_datacheckin", "p_datacheckout"]):
            logging.error("Faltam parametros!")
            return jsonify({"error": "Faltam parametros!"}), 400  # BAD_REQUEST

        # chamar funcao para fazer reserva
        message = manageReservas.insert_reserva(
            id_cliente,
            id_quarto,
            data['p_datacheckin'],
            data['p_datacheckout']
        )

        if "Reserva feita feita com sucesso!" in message:
            logging.info("reserva inserida com sucesso!")
            return jsonify({"message": message}), 201  # CREATED
        else:
            logging.error(f"Erro ao fazer reserva: {message}")
            return jsonify({"error": message}), 500  # INTERNAL_SERVER_ERROR

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@reservas_bp.route('/cancelar_reserva', methods=['POST'])
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
    
@reservas_bp.route('/ver_reservasCliente', methods=['POST'])
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
    
@reservas_bp.route('/ver_todasReservas', methods=['POST'])
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
    

@reservas_bp.route('/ver_seQuartoDisponivel', methods=['POST'])
def verSeDisponivel():
    try:
        data = request.get_json()

                #verificar se todos os parametros existem
        if not all(k in data for k in ["p_idquarto", "data_pretendida"]):
            logging.error("Faltam parametros!")

            #erro no postman
            return jsonify({"error": "Faltam parametros!"}), BAD_REQUEST
        
        if manageReservas.verDisponibilidadeQuarto(data["p_idquarto"], data["data_pretendida"]):
            logging.info("Quarto ocupado")

            return jsonify({"error": "Quarto n disponivel"}), CONFLICT
        else:
            logging.info("Quarto Disponivel")
            return jsonify({"message":"Quarto disponivel"}), 201  
        
    except Exception as e:
        return jsonify({"Erro"})
