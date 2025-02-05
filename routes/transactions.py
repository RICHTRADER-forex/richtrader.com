import locale
from flask import Blueprint, request, jsonify, session
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from database import engine, Usuario
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

transactions_bp = Blueprint('transactions', __name__)
Session = sessionmaker(bind=engine)



@transactions_bp.route('/admin/retirar', methods=['POST'])  # ✅
def admin_retirar():
    """Permite que administradores realizem retiradas via cURL"""

    # 🔹 Obter os dados enviados no cURL
    data = request.json
    email = data.get("email")
    senha = data.get("senha")
    iban = data.get("iban")
    valor = data.get("valor")

    # 🔹 Validar os dados recebidos
    if not email or not senha or not iban or not valor:
        return jsonify(
            {"success": False, "message": "Todos os campos são obrigatórios!"}), 400

    session_db = Session()

    # 🔹 Verificar se o e-mail pertence ao administrador
    admin = session_db.query(Usuario).filter_by(email=email).first()

    if not admin or not check_password_hash(admin.senha, senha):
        session_db.close()
        return jsonify(
            {"success": False, "message": "Credenciais inválidas!"}), 403

    # 🔹 Buscar o usuário pelo IBAN
    usuario = session_db.query(Usuario).filter_by(iban=iban).first()

    if not usuario:
        session_db.close()
        return jsonify(
            {"success": False, "message": "IBAN não encontrado!"}), 404

    # 🔹 Verificar se o saldo é suficiente
    if usuario.saldo < float(valor):
        session_db.close()
        return jsonify(
            {"success": False, "message": "Saldo insuficiente!"}), 400

    # 🔹 Atualizar o saldo do usuário
    usuario.saldo -= float(valor)

    # 🔹 Registrar a transação no banco de dados
    session_db.execute(
        text("INSERT INTO transacoes (usuario_id, tipo, valor) VALUES (:usuario_id, :tipo, :valor)"), {
            "usuario_id": usuario.id, "tipo": "saque", "valor": float(valor)}
    )

    session_db.commit()  # Certifique-se de que está na indentação correta
    session_db.close()


    return jsonify(
        {"success": True, "message": f"Retirada de € {valor} realizada com sucesso!"})


# Configurar para formato europeu (€ 21.200,00)
locale.setlocale(locale.LC_MONETARY, 'pt_PT.UTF-8')



# 🔹 Rota da página de retirada
@transactions_bp.route('/retirada')
def retirada():
    if 'user_id' not in session:
        return redirect('/login')

    return render_template('retirada.html')

# 🔹 Validação do IBAN antes da retirada


@transactions_bp.route('/validar_iban_retirada', methods=['POST'])
def validar_iban_retirada():
    data = request.json
    iban_digitado = data.get("iban")

    if not iban_digitado:
        return jsonify(
            {"success": False, "message": "IBAN não fornecido!"}), 400

    session_db = Session()
    usuario = session_db.query(Usuario).filter_by(iban=iban_digitado).first()
    session_db.close()

    if usuario:
        return jsonify({"success": True,
                        "message": f"IBAN Válido: {usuario.nome}"})
    else:
        return jsonify({"success": False, "message": "IBAN inválido!"}), 404

# 🔹 Rota para processar retirada e enviar e-mail


@transactions_bp.route('/processar_retirada', methods=['POST'])
def processar_retirada():
    if 'user_id' not in session:
        return jsonify(
            {"success": False, "message": "Usuário não autenticado!"}), 401

    usuario_id = session['user_id']
    session_db = Session()

    # 🔹 Recuperar o usuário associado ao ID de sessão
    usuario = session_db.query(Usuario).filter_by(id=usuario_id).first()

    if not usuario:
        session_db.close()
        return jsonify(
            {"success": False, "message": "Usuário não encontrado!"}), 404

    # 🔹 Obter dados do formulário
    valor = request.form.get("valor")
    iban = request.form.get("iban")

    if not valor or not iban:
        return jsonify(
            {"success": False, "message": "Todos os campos são obrigatórios!"}), 400

    # Verificar se o IBAN pertence ao usuário
    if usuario.iban != iban:
        return jsonify(
            {"success": False, "message": "IBAN não corresponde ao usuário autenticado!"}), 403

    # Enviar e-mail com os detalhes da retirada
    try:
        email_empresa = "richtradereps@gmail.com"
        senha_email = "goydceutzacjuezq"  # Substitua pela senha do seu e-mail
        destinatario = email_empresa

        mensagem = MIMEMultipart()
        mensagem["From"] = email_empresa
        mensagem["To"] = destinatario
        mensagem["Subject"] = "Nova Solicitação de Retirada"

        corpo_email = f"""
        <h2>Detalhes da Retirada</h2>
        <p><strong>Nome:</strong> {usuario.nome}</p>
        <p><strong>Email:</strong> {usuario.email}</p>
        <p><strong>IBAN:</strong> {usuario.iban}</p>
        <p><strong>Valor:</strong> € {valor}</p>
        """

        mensagem.attach(MIMEText(corpo_email, "html"))

        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(email_empresa, senha_email)
        servidor.sendmail(email_empresa, destinatario, mensagem.as_string())
        servidor.quit()

        session_db.close()
        return jsonify({"success": True,
                        "message": "Retirada processada com sucesso!"})

    except Exception as e:
        session_db.close()
        return jsonify(
            {"success": False, "message": f"Erro ao enviar e-mail: {str(e)}"}), 500

# 🔹 Rota para processar depósito e enviar e-mail
@transactions_bp.route('/processar_deposito', methods=['POST'])
def processar_deposito():
    try:
        if 'user_id' not in session:
            return jsonify(
                {"success": False, "message": "Usuário não autenticado!"}), 401

        usuario_id = session['user_id']
        session_db = Session()
        usuario = session_db.query(Usuario).filter_by(id=usuario_id).first()

        if not usuario:
            session_db.close()
            return jsonify(
                {"success": False, "message": "Usuário não encontrado!"}), 404

        dados = request.form
        metodo = dados.get("metodo")
        valor = dados.get("valor")
        comprovante = request.files.get("comprovante")
        iban = dados.get("iban")

        if not metodo or not valor or not comprovante or not iban:
            return jsonify(
                {"success": False, "message": "Todos os campos são obrigatórios!"}), 400

        # 🔹 Validar IBAN no banco de dados
        usuario_iban = session_db.query(Usuario).filter_by(iban=iban).first()
        if not usuario_iban:
            return jsonify(
                {"success": False, "message": "IBAN inválido!"}), 400

        # 🔹 Criar diretório de comprovantes se não existir
        diretorio_comprovantes = "static/comprovantes"
        if not os.path.exists(diretorio_comprovantes):
            os.makedirs(diretorio_comprovantes)

        # 🔹 Salvar o comprovante
        caminho_comprovante = os.path.join(
            diretorio_comprovantes, f"{
                usuario.iban}_{
                comprovante.filename}")
        comprovante.save(caminho_comprovante)

        # 🔹 Enviar e-mail com o comprovante anexado
        try:
            email_empresa = "richtradereps@gmail.com"
            senha_email = "goydceutzacjuezq"  # 🔹 Substituir por uma senha de aplicativo válida
            destinatario = email_empresa
            mensagem = MIMEMultipart()
            mensagem["From"] = email_empresa
            mensagem["To"] = destinatario
            mensagem["Subject"] = "Novo Depósito Recebido"

            corpo_email = f"""
            <h2>Detalhes do Depósito</h2>
            <p><strong>Nome:</strong> {usuario.nome}</p>
            <p><strong>Email:</strong> {usuario.email}</p>
            <p><strong>IBAN:</strong> {usuario.iban}</p>
            <p><strong>Valor:</strong> € {valor}</p>
            <p><strong>Método:</strong> {metodo}</p>
            """

            mensagem.attach(MIMEText(corpo_email, "html"))

            # 🔹 Anexar o comprovante
            with open(caminho_comprovante, "rb") as anexo:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(anexo.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={
                        comprovante.filename}")
                mensagem.attach(part)

            # 🔹 Enviar e-mail
            servidor = smtplib.SMTP("smtp.gmail.com", 587)
            servidor.starttls()
            servidor.login(email_empresa, senha_email)
            servidor.sendmail(
                email_empresa,
                destinatario,
                mensagem.as_string())
            servidor.quit()

        except Exception as e:
            return jsonify(
                {"success": False, "message": f"Erro ao enviar e-mail: {str(e)}"}), 500

        session_db.close()

        return jsonify({"success": True,
                        "message": "Depósito processado com sucesso!"})

    except Exception as e:
        print("Erro no processamento do depósito:", e)
        return jsonify(
            {"success": False, "message": f"Erro interno no servidor: {str(e)}"}), 500








# 🔹 Rota da Página de Depósito
@transactions_bp.route('/admin/depositar', methods=['POST'])
def admin_depositar():
    try:
        print("📢 [LOG] Recebendo solicitação de depósito...")

        admin_email = "richtradereps@gmail.com"
        auth_email = request.json.get("email")
        auth_senha = request.json.get("senha")

        if auth_email != admin_email:
            return jsonify({"success": False, "message": "Acesso negado!"}), 403

        session_db = Session()  # 🔹 Criamos uma sessão ativa
        admin_user = session_db.query(Usuario).filter_by(email=auth_email).first()

        if not admin_user or not check_password_hash(admin_user.senha, auth_senha):
            session_db.close()
            return jsonify({"success": False, "message": "Senha incorreta!"}), 401

        iban = request.json.get("iban")
        valor = request.json.get("valor")

        if not iban or not valor or float(valor) <= 0:
            session_db.close()
            return jsonify({"success": False, "message": "IBAN e valor são obrigatórios!"}), 400

        # 🔹 Buscar usuário dentro da mesma sessão
        usuario = session_db.query(Usuario).filter_by(iban=iban).first()

        if not usuario:
            session_db.close()
            return jsonify({"success": False, "message": "IBAN não encontrado!"}), 404

        # 🔹 Atualizar saldo dentro da sessão ativa
        usuario.saldo += float(valor)
        session_db.add(usuario)  # 🔹 Garante que a mudança do saldo seja registrada

        # 🔹 Registrar transação na tabela `transacoes`
        session_db.execute(text(
            "INSERT INTO transacoes (usuario_id, tipo, valor) VALUES (:usuario_id, 'deposito', :valor)"
        ), {"usuario_id": usuario.id, "valor": valor})

        session_db.commit()  # 🔹 Confirma a transação no banco
        session_db.refresh(usuario)  # 🔹 Atualiza os dados do usuário na sessão
        session_db.close()  # 🔹 Fecha a sessão somente agora

        print(f"✅ [SUCESSO] Depósito de €{valor} realizado para {usuario.nome}!")

        return jsonify({"success": True, "message": f"Depósito de €{valor} realizado para {usuario.nome}!"})

    except Exception as e:
        print(f"⛔ [ERRO CRÍTICO] {str(e)}")  # 🔹 Exibe erro no terminal
        return jsonify({"success": False, "message": f"Erro interno no servidor: {str(e)}"}), 500






@transactions_bp.route('/admin/consultar_transacoes', methods=['POST'])
def consultar_transacoes():
    try:
        # 🔹 Log para depuração
        print("📢 [LOG] Recebendo solicitação de consulta de transações...")

        admin_email = "richtradereps@gmail.com"
        auth_email = request.json.get("email")
        auth_senha = request.json.get("senha")

        # 🔹 Verifica se o usuário é administrador
        if auth_email != admin_email:
            print("⛔ [ERRO] Acesso negado! Email inválido.")  # 🔹 Depuração
            return jsonify(
                {"success": False, "message": "Acesso negado!"}), 403

        session_db = Session()
        admin_user = session_db.query(
            Usuario).filter_by(email=auth_email).first()

        if not admin_user:
            print("⛔ [ERRO] Admin não encontrado!")  # 🔹 Depuração
            session_db.close()
            return jsonify(
                {"success": False, "message": "Admin não encontrado!"}), 404

        print("📢 [LOG] Verificando senha...")  # 🔹 Depuração
        if not check_password_hash(admin_user.senha, auth_senha):
            print("⛔ [ERRO] Senha incorreta!")  # 🔹 Depuração
            session_db.close()
            return jsonify(
                {"success": False, "message": "Senha incorreta!"}), 401

        # 🔹 Captura o IBAN do usuário a ser consultado
        iban = request.json.get("iban")

        if not iban:
            print("⛔ [ERRO] IBAN não fornecido!")  # 🔹 Depuração
            return jsonify(
                {"success": False, "message": "IBAN é obrigatório!"}), 400

        # 🔹 Busca o usuário pelo IBAN
        usuario = session_db.query(Usuario).filter_by(iban=iban).first()

        if not usuario:
            print("⛔ [ERRO] IBAN não encontrado!")  # 🔹 Depuração
            session_db.close()
            return jsonify(
                {"success": False, "message": "IBAN não encontrado!"}), 404

        # 🔹 Consulta o saldo do usuário
        saldo = usuario.saldo
        session_db.close()  # Fecha a sessão após a consulta

        print(
            f"✅ [SUCESSO] Saldo do usuário {
                usuario.nome}: €{saldo}")  # 🔹 Confirmação

        return jsonify({
            "success": True,
            "message": f"Consulta realizada com sucesso!",
            "usuario": usuario.nome,
            "iban": usuario.iban,
            "saldo": saldo
        })

    except Exception as e:
        print(f"⛔ [ERRO CRÍTICO] {str(e)}")  # 🔹 Exibe erro no terminal
        return jsonify(
            {"success": False, "message": f"Erro interno no servidor: {str(e)}"}), 500

@transactions_bp.route('/admin/consultar_extrato', methods=['POST'])
def consultar_extrato():
    try:
        print("📢 [LOG] Recebendo solicitação de extrato...")

        admin_email = "richtradereps@gmail.com"
        auth_email = request.json.get("email")
        auth_senha = request.json.get("senha")

        if auth_email != admin_email:
            return jsonify({"success": False, "message": "Acesso negado!"}), 403

        session_db = Session()
        admin_user = session_db.query(Usuario).filter_by(email=auth_email).first()

        if not admin_user or not check_password_hash(admin_user.senha, auth_senha):
            session_db.close()
            return jsonify({"success": False, "message": "Senha incorreta!"}), 401

        iban = request.json.get("iban")

        if not iban:
            return jsonify({"success": False, "message": "IBAN é obrigatório!"}), 400

        usuario = session_db.query(Usuario).filter_by(iban=iban).first()

        if not usuario:
            session_db.close()
            return jsonify({"success": False, "message": "IBAN não encontrado!"}), 404

        # 🔹 Buscar transações do usuário
        transacoes = session_db.execute(text(
            "SELECT tipo, valor, data FROM transacoes WHERE usuario_id = :usuario_id ORDER BY data DESC"
        ), {"usuario_id": usuario.id}).fetchall()

        session_db.close()

        # 🔹 Formatar valores monetários para exibição
        extrato = [{"tipo": t[0], "valor": locale.format_string('%.2f', t[1], grouping=True), "data": t[2]} for t in transacoes]
        saldo_formatado = locale.format_string('%.2f', usuario.saldo, grouping=True)  # 🔹 Formata o saldo corretamente

        return jsonify({
            "success": True,
            "message": "Consulta de extrato realizada com sucesso!",
            "usuario": usuario.nome,
            "iban": usuario.iban,
            "saldo": saldo_formatado,  # 🔹 Saldo formatado corretamente
            "extrato": extrato
        })

    except Exception as e:
        return jsonify({"success": False, "message": f"Erro interno no servidor: {str(e)}"}), 500


@transactions_bp.route('/deposito')
def deposito():
    if not usuario_logado():
        return redirect('/login')

    return render_template('deposito.html')

# 🔹 Rota para validar o IBAN e retornar o nome do usuário
@transactions_bp.route('/validar_iban', methods=['POST'])
def validar_iban():
    data = request.json
    iban_digitado = data.get("iban")

    if not iban_digitado:
        return jsonify(
            {"success": False, "message": "IBAN não fornecido!"}), 400

    session_db = Session()
    usuario = session_db.query(Usuario).filter_by(iban=iban_digitado).first()
    session_db.close()

    if usuario:
        return jsonify({"success": True,
                        "message": f"IBAN Válido: {usuario.nome}"})
    else:
        return jsonify({"success": False, "message": "IBAN inválido!"}), 404



