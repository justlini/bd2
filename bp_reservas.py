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
    
    