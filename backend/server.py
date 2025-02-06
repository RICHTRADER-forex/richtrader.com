from flask import Flask, request, jsonify
import smtplib
import random
from email.mime.text import MIMEText

# Importações ajustadas corretamente
from backend.Banco_de_dados.config_db import get_db_connection
from Banco_de_dados.utils import gerar_iban

app = Flask(__name__)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "richtradereps@gmail.com"
EMAIL_PASSWORD = "goydceutzacjuezq"

def enviar_email_confirmacao(email, codigo):
    """ Envia um e-mail com o código de confirmação """
    msg = MIMEText(f"Seu código de confirmação é: {codigo}")
    msg["Subject"] = "Confirme seu Cadastro"
    msg["From"] = EMAIL_SENDER
    msg["To"] = email

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False

@app.route('/cadastro', methods=['POST'])
def cadastrar_usuario():
    data = request.json
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    if not nome or not email or not senha:
        return jsonify({"erro": "Todos os campos são obrigatórios!"}), 400

    iban = gerar_iban()
    codigo_confirmacao = str(random.randint(100000, 999999))

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (nome, email, senha, iban, codigo_confirmacao) VALUES (%s, %s, %s, %s, %s)",
                    (nome, email, senha, iban, codigo_confirmacao))
        conn.commit()
        cur.close()
        conn.close()

        if enviar_email_confirmacao(email, codigo_confirmacao):
            return jsonify({"mensagem": "Cadastro realizado! Verifique seu e-mail para confirmação.", "iban": iban}), 201
        else:
            return jsonify({"erro": "Erro ao enviar e-mail de confirmação."}), 500

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/confirmar_email', methods=['POST'])
def confirmar_email():
    data = request.json
    email = data.get('email')
    codigo = data.get('codigo')

    if not email or not codigo:
        return jsonify({"erro": "Todos os campos são obrigatórios!"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT codigo_confirmacao FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()

        if not usuario:
            return jsonify({"erro": "Usuário não encontrado."}), 404

        if usuario[0] == codigo:
            cur.execute("UPDATE usuarios SET confirmado = TRUE WHERE email = %s", (email,))
            conn.commit()
            return jsonify({"mensagem": "E-mail confirmado com sucesso! Você já pode fazer login."}), 200
        else:
            return jsonify({"erro": "Código incorreto."}), 400

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)