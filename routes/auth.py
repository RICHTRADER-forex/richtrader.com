from flask import Blueprint, render_template, request, redirect, session, jsonify, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import sessionmaker
from database import engine, Usuario
from utils import gerar_iban

auth_bp = Blueprint('auth', __name__)
Session = sessionmaker(bind=engine)


# ✅ Rota para Cadastro de Usuário
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    session_db = Session()
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')

    if not nome or not email or not senha:
        return jsonify({"success": False, "message": "Todos os campos são obrigatórios!"}), 400

    # 🔹 Verificar se o e-mail já existe
    usuario_existente = session_db.query(Usuario).filter_by(email=email).first()
    if usuario_existente:
        session_db.close()
        return jsonify({"success": False, "message": "Email já cadastrado!"}), 400

    # 🔹 Criptografar a senha e gerar um IBAN único
    senha_hash = generate_password_hash(senha)
    novo_iban = gerar_iban()

    # 🔹 Criar novo usuário com saldo inicial 0.00
    novo_usuario = Usuario(
        nome=nome.strip(),
        email=email.strip(),
        senha=senha_hash,
        iban=novo_iban,
        saldo=0.00  # ✅ Agora o saldo começa em zero
    )
    session_db.add(novo_usuario)
    session_db.commit()
    session_db.close()

    return jsonify({"success": True, "iban": novo_iban}), 201


# ✅ Rota para Login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form.get('email')
    senha = request.form.get('senha')

    if not email or not senha:
        return jsonify({"success": False, "message": "E-mail e senha são obrigatórios!"}), 400

    session_db = Session()
    usuario = session_db.query(Usuario).filter_by(email=email).first()
    session_db.close()

    if usuario and check_password_hash(usuario.senha, senha):
        session.permanent = True  # 🔥 Faz a sessão durar mais tempo
        session['user_id'] = usuario.id
        session['user_name'] = usuario.nome
        session['user_email'] = usuario.email
        session['user_iban'] = usuario.iban

        print("Sessão após login:", session)

        return jsonify({"success": True}), 200  

    return jsonify({"success": False, "message": "E-mail ou senha inválidos."}), 401

# ✅ Rota para Logout
@auth_bp.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('auth.login'))  # ✅ Agora redireciona corretamente
