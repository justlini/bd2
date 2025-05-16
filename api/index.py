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
                background: url('https://www.google.pt/url?sa=i&url=https%3A%2F%2Fwww.noticiasaominuto.com%2Ffama%2F926490%2Fvideo-fernando-mendes-fica-em-tronco-nu-em-pleno-programa&psig=AOvVaw1EA9qB2KWMaJGhMYUKfjgf&ust=1747491599470000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCNjehdKXqI0DFQAAAAAdAAAAABAE') no-repeat center center fixed;
                background-size: cover;
                background-color: #ff2d87;
                color: #fff;
                margin: 0;
                padding: 0;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: rgba(255, 45, 135, 0.92);
                border-radius: 18px;
                box-shadow: 0 4px 32px rgba(255,45,135,0.18);
                padding: 44px 36px 36px 36px;
                text-align: center;
                max-width: 440px;
                margin: 32px;
            }
            h1 {
                font-size: 2.7rem;
                color: #fff;
                margin-bottom: 0.5em;
                letter-spacing: 1px;
                text-shadow: 0 2px 12px #ff2d87cc;
            }
            .autores {
                margin-top: 1.5em;
                font-size: 1.15rem;
                color: #fff;
            }
            .fernando-anim {
                margin: 32px auto 0 auto;
                width: 180px;
                height: 180px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .fernando-anim img {
                width: 100%;
                height: 100%;
                border-radius: 50%;
                border: 4px solid #fff;
                box-shadow: 0 2px 18px #ff2d87cc;
                background: #fff;
                object-fit: cover;
            }
            @media (max-width: 600px) {
                .container { max-width: 98vw; padding: 18px 4vw; }
                .fernando-anim { width: 120px; height: 120px; }
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
                <img src="https://media1.tenor.com/m/EFDwfjT2GuQAAAAd/spinning-cat.gif" alt="Fernando Mendes">
            </div>
            <p style="margin-top:1.5em; color:#fff; font-size:0.98em; text-shadow:0 1px 8px #ff2d87cc;">
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
