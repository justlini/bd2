import os
import psycopg2
from flask import Flask, jsonify, request
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
from datetime import timedelta
import logging
import bcrypt

# Configuração do Flask
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=60)
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



@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trabalho Base de Dados 2</title>
        <style>
            body {
                font-family: sans-serif;
                color: #000000;
                margin: 10px;
                padding: 10px;
            }
            
            h1 {
                font-size: 32px;
                color: blue;
            }
            
            p {
                font-size: 16px;
                color: #333333;
            }
        </style>
    </head>
    <body>
        <div>
            <h1>Trabalho Base de Dados 2</h1>
            <p>Trabalho realizado por:</p>
            <p>Alexandre Brito</p>
            <p>Miguel Plácido</p>
        </div>
    </body>
    </html>
    """

#routes
app.register_blueprint(reservas_bp)

app.register_blueprint(transacoes_bp)

app.register_blueprint(utilizadores_bp)

app.register_blueprint(quartos_bp)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
