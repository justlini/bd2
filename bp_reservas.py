from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from api.conn import BaseDeDados
from reservas import ManageReservas

reservas_bp = Blueprint('reservas', __name__)


manageReservas = ManageReservas()


@app.route('/pagar_reserva/<int:id_reserva>', methods=['POST'])
@jwt_required()
def pagar_reserva(id_reserva):
    try:
        user = get_jwt_identity()
        
        if user['tipo'] not in ['admin', 'rececionista']:
            logging.error("Unauthorized access attempt.")
            return jsonify({"error": "Unauthorized"}), BAD_REQUEST

        # Chamar a função para pagar a reserva
        message = manageReservas.pagar_reserva(id_reserva)

        if "Reserva paga com sucesso!" in message:
            logging.info("Reserva paga com sucesso!")
            return jsonify({"message": message}), CREATED
        else:
            logging.error(f"Erro ao pagar reserva: {message}")
            return jsonify({"error": message}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR
