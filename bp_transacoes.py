from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.conn import BaseDeDados
import logging
from transacoes import ManageTransacoes

OK_CODE = 200
BAD_REQUEST = 400
CONFLICT = 409
INTERNAL_SERVER_ERROR = 500
CREATED = 201


transacoes_bp = Blueprint('transacoes', __name__)

manageTransacoes = ManageTransacoes()

@transacoes_bp.route('/ver_pagamentos', methods=['POST'])
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


@transacoes_bp.route('/ver_pagamentos_cliente', methods=['POST'])
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
    