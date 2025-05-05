from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.conn import BaseDeDados
import logging
from reservas import ManageReservas

# Create the Blueprint
reservas_bp = Blueprint('reservas', __name__)

manageReservas = ManageReservas()

# Define the route using the Blueprint
@reservas_bp.route('/pagar_reserva/<int:id_reserva>', methods=['POST'])
@jwt_required()
def pagar_reserva(id_reserva):
    try:
        user = get_jwt_identity()
        
        if user['tipo'] not in ['admin', 'rececionista']:
            logging.error("Unauthorized access attempt.")
            return jsonify({"error": "Unauthorized"}), 400  # BAD_REQUEST

        # Call the function to pay for the reservation
        message = manageReservas.pagar_reserva(id_reserva)

        if "Reserva paga com sucesso!" in message:
            logging.info("Reserva paga com sucesso!")
            return jsonify({"message": message}), 201  # CREATED
        else:
            logging.error(f"Erro ao pagar reserva: {message}")
            return jsonify({"error": message}), 500  # INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500  # INTERNAL_SERVER_ERROR
    
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