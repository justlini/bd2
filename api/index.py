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
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trabalho Base de Dados 2</title>
        <style>
            body {
                font-family: 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
                color: #222;
                margin: 0;
                padding: 0;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: #fff;
                border-radius: 16px;
                box-shadow: 0 4px 24px rgba(0,0,0,0.08);
                padding: 40px 32px 32px 32px;
                text-align: center;
                max-width: 420px;
            }
            h1 {
                font-size: 2.5rem;
                color: #1976d2;
                margin-bottom: 0.5em;
            }
            .autores {
                margin-top: 1.5em;
                font-size: 1.1rem;
                color: #444;
            }
            .fernando-anim {
                margin: 32px auto 0 auto;
                width: 180px;
                height: 180px;
                display: flex;
                align-items: center;
                justify-content: center;
                animation: rodar 3s linear infinite;
            }
            @keyframes rodar {
                0% { transform: rotate(0deg);}
                100% { transform: rotate(360deg);}
            }
            .fernando-anim img {
                width: 100%;
                height: 100%;
                border-radius: 50%;
                border: 4px solid #1976d2;
                box-shadow: 0 2px 12px rgba(25,118,210,0.15);
                background: #fff;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Trabalho Base de Dados 2</h1>
            <div class="autores">
                <p>Trabalho realizado por:</p>
                <p><b>Alexandre Brito</b></p>
                <p><b>Miguel Plácido</b></p>
            </div>
            <div class="fernando-anim">
                <img src="/static/fernando.gif" alt="Fernando Mendes a rodar">
            </div>
            <p style="margin-top:1.5em; color:#888; font-size:0.95em;">
                Powered by Flask &mdash; O Preço Certo!
            </p>
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
