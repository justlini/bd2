from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.conn import BaseDeDados
import logging
from transacoes import ManageTransacoes
from auditoria import ManageAuditoria
from datetime import datetime
OK_CODE = 200
BAD_REQUEST = 400
CONFLICT = 409
INTERNAL_SERVER_ERROR = 500
CREATED = 201


transacoes_bp = Blueprint('transacoes', __name__)

manageTransacoes = ManageTransacoes()
manageAuditoria = ManageAuditoria()

@transacoes_bp.route('/ver_pagamentos', methods=['GET'])
@jwt_required()
def ver_pagamentos():
    try:
        user = get_jwt_identity()
        p_utilizador_app = user['nome']
        p_utilizador_bd = user['db_user']
        p_dataLog = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if user['tipo'] not in ['admin']:
            logging.error("Tentativa de acesso não autorizado.")
            return jsonify({"error": "Unauthorized"}), BAD_REQUEST
        
        # Chamar a função para ver todos os pagamentos
        pagamentos = manageTransacoes.ver_pagamentos()

        if pagamentos:
            logging.info("Todos os pagamentos obtidos com sucesso!")
            log_message = f"Ver todos os pagamentos"
            manageAuditoria.insert_Log(p_utilizador_bd,p_utilizador_app,p_dataLog,log_message)
            return jsonify({"pagamentos": pagamentos}), OK_CODE
        else:
            logging.error("Erro ao obter todos os upagamentos.")
            # erro no postman
            return jsonify({"error": "Erro ao obter todos os pagamentos."}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR


@transacoes_bp.route('/ver_pagamentos_cliente/<int:p_idcliente>', methods=['GET'])
@jwt_required()
def ver_pagamentos_cliente(p_idcliente):
    try:
        user = get_jwt_identity()
        p_utilizador_app = user['nome']
        p_utilizador_bd = user['db_user']
        p_dataLog = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if user['tipo'] not in ['admin', 'cliente']:
            logging.error("Tentativa de acesso não autorizado.")
            return jsonify({"error": "Unauthorized"}), BAD_REQUEST
        
        if user['tipo'] == 'cliente' and p_idcliente != user['idcliente']:
            logging.error("Tentativa de acesso não autorizado.")
            return jsonify({"error": "Unauthorized"}), BAD_REQUEST

        # Chamar a função para ver os pagamentos do cliente
        pagamentos = manageTransacoes.verpagamentos_cliente(p_idcliente)

        if pagamentos:
            logging.info("Pagamentos do cliente obtidos com sucesso!")
            log_message = f"Viu pagamentos do cliente com ID: {p_idcliente}"
            manageAuditoria.insert_Log(p_utilizador_bd, p_utilizador_app, p_dataLog, log_message)
            return jsonify({"pagamentos": pagamentos}), OK_CODE
        else:
            logging.error("Erro ao obter pagamentos do cliente.")
            return jsonify({"error": "Erro ao obter pagamentos do cliente."}), INTERNAL_SERVER_ERROR
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), INTERNAL_SERVER_ERROR
