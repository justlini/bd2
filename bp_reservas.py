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


reservas_bp = Blueprint('reservas', __name__)

manageReservas = ManageReservas()
manageAuditoria = ManageAuditoria()

@reservas_bp.route('/pagar_reserva/<int:id_reserva>', methods=['GET'])
@jwt_required()
def pagar_reserva(id_reserva):
    try:
        user = get_jwt_identity()
        p_utilizador_app = user['nome']
        p_utilizador_bd = user['db_user']
        p_dataLog = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if user['tipo'] not in ['admin', 'rececionista']:
            logging.error("tentativa de acesso não autorizado.")
            return jsonify({"error": "Unauthorized"}), 400 
        
        # Obter a mensagem da função de pagar reserva
        message = manageReservas.pagar_reserva(id_reserva)

        log_message = f"Pagar reserva: {id_reserva}"
        manageAuditoria.insert_Log(p_utilizador_bd, p_utilizador_app, p_dataLog, log_message)

        if "paga com sucesso" in message.lower():
            logging.info("Reserva paga com sucesso!")
            return jsonify({"message": message}), 201
        else:
            logging.error(f"Erro ao pagar reserva: {message}")
            return jsonify({"error": message}), 500 
    except Exception as e:
        logging.error(f"Erro nao esperado: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
    
@reservas_bp.route('/reserva/<int:id_cliente>/<int:id_quarto>/inserir', methods=['POST'])
@jwt_required()
def registar_reserva(id_cliente, id_quarto):
    try:
        user = get_jwt_identity()
        p_utilizador_app = user['nome']
        p_utilizador_bd = user['db_user']
        p_dataLog = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        log_message = f"Registar reserva: {id_quarto}"
        manageAuditoria.insert_Log(p_utilizador_bd,p_utilizador_app,p_dataLog,log_message)

        if "Reserva feita feita com sucesso!" in message:
            logging.info("reserva inserida com sucesso!")
            return jsonify({"message": message}), 201  # CREATED
        else:
            logging.error(f"Erro ao fazer reserva: {message}")
            return jsonify({"error": message}), 500  # INTERNAL_SERVER_ERROR

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@reservas_bp.route('/cancelar_reserva/<int:p_idreserva>', methods=['GET'])
@jwt_required()
def cancelar_reserva(p_idreserva):
    try:
        user = get_jwt_identity()
        p_utilizador_app = user['nome']
        p_utilizador_bd = user['db_user']
        p_dataLog = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if user['tipo'] not in ['admin', 'rececionista']:
            logging.error("Unauthorized access attempt.")
            return jsonify({"error": "Unauthorized"}), BAD_REQUEST

        # Chamar a função para cancelar a reserva
        message = manageReservas.cancelar_reserva(p_idreserva)

        log_message = f"Cancelar reserva: {p_idreserva}"
        manageAuditoria.insert_Log(p_utilizador_bd, p_utilizador_app, p_dataLog, log_message)

        if "cancelada com sucesso" in message.lower():
            logging.info(f"Reserva cancelada com sucesso: {p_idreserva}")
            return jsonify({"message": message}), CREATED
        else:
            logging.error(f"Erro ao cancelar reserva: {message}")
            return jsonify({"error": message}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR
    
@reservas_bp.route('/ver_reservasCliente/<int:p_idcliente>', methods=['GET'])
@jwt_required()
def ver_reservas_cliente(p_idcliente):
    try:
        user = get_jwt_identity()
        p_utilizador_app = user['nome']
        p_utilizador_bd = user['db_user']
        p_dataLog = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if user['tipo'] not in ['admin', 'rececionista', 'cliente']:
            logging.error("Acesso não autorizado.")
            return jsonify({"error": "Acesso não autorizado"}), BAD_REQUEST
        
        if user['tipo'] == 'cliente' and p_idcliente != user['idcliente']:
            logging.error("Aviso: Cliente não autorizado a ver reservas de outro cliente.")
            return jsonify({"error": "Nao autorizado"}), BAD_REQUEST

        # Chamar a função para ver as reservas do cliente
        reservas = manageReservas.ver_reservasCliente(p_idcliente)

        log_message = f"Ver reserva cliente ID: {p_idcliente}"
        manageAuditoria.insert_Log(p_utilizador_bd, p_utilizador_app, p_dataLog, log_message)

        if reservas:
            logging.info("Reservas do cliente obtidas com sucesso!")
            return jsonify({"reservas": reservas}), OK_CODE
        else:
            logging.error("Erro ao obter reservas do cliente.")
            return jsonify({"error": "Erro ao obter reservas do cliente."}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR
    
@reservas_bp.route('/ver_todasReservas', methods=['GET'])
@jwt_required()
def ver_todas_reservas():
    try:
        user = get_jwt_identity()
        
        if user['tipo'] not in ['admin']:
            logging.error("Tentativa de acesso não autorizado.")
            return jsonify({"error": "Nao autorizado"}), BAD_REQUEST

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
@jwt_required()
def verSeDisponivel():
    try:
        data = request.get_json()
        user = get_jwt_identity()
        p_utilizador_app = user['nome']
        p_utilizador_bd = user['db_user']
        p_dataLog = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                #verificar se todos os parametros existem
        if not all(k in data for k in ["p_idquarto", "data_pretendida"]):
            logging.error("Faltam parametros!")

            #erro no postman
            return jsonify({"error": "Faltam parametros!"}), BAD_REQUEST
        
        log_message = f"Ver reserva Quarto disponivel: {data['p_idquarto']}"
        manageAuditoria.insert_Log(p_utilizador_bd, p_utilizador_app, p_dataLog, log_message)
        
        if manageReservas.verDisponibilidadeQuarto(data["p_idquarto"], data["data_pretendida"]):
            logging.info("Quarto ocupado")

            return jsonify({"error": "Quarto n disponivel"}), CONFLICT
        
        
        if user['tipo'] not in ['admin', 'rececionista', 'cliente']:
            logging.error("Tentativa de acesso não autorizado.")
            return jsonify({"error": "Unauthorized"}), BAD_REQUEST
        
        else:
            logging.info("Quarto Disponivel")
            return jsonify({"message":"Quarto disponivel"}), 201  
        
    except Exception as e:
        return jsonify({"Erro"})
