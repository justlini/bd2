from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.conn import BaseDeDados
import logging
from reservas import ManageReservas

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'olamundo' #os.getenv('JWT_SECRET')
jwt = JWTManager(app)
utilizadores = Utilizadores()
manageQuartos = ManageQuartos()
manageReservas = ManageReservas()
# Códigos HTTP
OK_CODE = 200
BAD_REQUEST = 400
CONFLICT = 409
INTERNAL_SERVER_ERROR = 500
CREATED = 201

bd = BaseDeDados()

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
