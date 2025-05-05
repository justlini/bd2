from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.conn import BaseDeDados
import logging
from quartos import ManageQuartos


OK_CODE = 200
BAD_REQUEST = 400
CONFLICT = 409
INTERNAL_SERVER_ERROR = 500
CREATED = 201


# Create the Blueprint
quartos_bp = Blueprint('quartos', __name__)

manageQuartos = ManageQuartos()

@quartos_bp.route('/mudarPrecoQuarto', methods=['POST'])
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

@quartos_bp.route('/mudarTipoQuarto', methods=['POST'])
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

@quartos_bp.route('/get_ImagensQuarto', methods=['POST'])
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

@quartos_bp.route('/upload_imagem_quarto', methods=['POST'])
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

@quartos_bp.route('/ver_disponibilidade_quarto', methods=['GET'])
def ver_disponibilidade_quarto_route():
    try:
        disponibilidade = manageQuartos.ver_disponibilidade_quarto()
        return jsonify({"disponibilidade": disponibilidade}), OK_CODE
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR
       


@quartos_bp.route('/inserir_quarto', methods=['POST'])
def registar_quarto():
    try:
        data = request.get_json()

        # Validate input parameters
        if not all(k in data for k in ["p_numeroquarto", "p_precoquarto", "p_tipoquarto"]):
            logging.error("Faltam parametros!")
            return jsonify({"error": "Faltam parametros!"}), BAD_REQUEST

        # Check if the room already exists
        if manageQuartos.quarto_exists(data["p_numeroquarto"]):
            logging.error("Quarto com esse numero já existe!")
            return jsonify({"error": "Quarto com esse numero já existe!"}), CONFLICT

        # Validate room type
        if data["p_tipoquarto"] not in ["casal", "solteiro"]:
            logging.error("Tipo de quarto invalido!")
            return jsonify({"error": "Tipo de quarto invalido!"}), BAD_REQUEST

        # Call the insert_quarto function
        message = manageQuartos.insert_quarto(
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