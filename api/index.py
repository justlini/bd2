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
from bp_transacoes import transacoes_bp
from bp_utilizadores import utilizadores_bp
from bp_quartos import quartos_bp
import logging
import bcrypt

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

# caminho para ir buscar as variaveis de ambiente

app.register_blueprint(reservas_bp)

app.register_blueprint(transacoes_bp)

app.register_blueprint(utilizadores_bp)

app.register_blueprint(quartos_bp)

# Rota para login de usuário

# Execução do aplicativo Flask
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
