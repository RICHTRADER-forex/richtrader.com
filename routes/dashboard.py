from flask import Blueprint, render_template, session, redirect, jsonify
from sqlalchemy.orm import sessionmaker
from database import engine, Session, Usuario, Ordem  # ✅ Importando corretamente
from utils import login_required
from datetime import datetime
import pytz

# Criando o Blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# Criando a sessão do banco de dados
Session = sessionmaker(bind=engine)

# ✅ Rota protegida do Dashboard
@dashboard_bp.route('/dashboard')
@login_required  # ✅ Protegendo a rota
def dashboard():
    if 'user_id' not in session:
        print("❌ [DEBUG] Usuário não está logado, redirecionando para login.")
        return redirect('/login')

    # 🔍 Debug: Exibir sessão atual
    print(f"📌 Sessão do usuário antes da consulta: {session}")

    usuario_id = session.get("user_id")

    if not usuario_id:
        print("❌ Usuário não encontrado na sessão!")
        return redirect('/login')

    # 🔹 Consulta ao banco
    session_db = Session()
    usuario = session_db.query(Usuario).filter(Usuario.id == usuario_id).first()
    session_db.close()

    if not usuario:
        print(f"❌ Nenhum usuário encontrado com ID {usuario_id}!")
        return redirect('/login')

    # 🔹 Confirmação dos dados carregados
    print(f"✅ Usuário carregado: {usuario.nome} - {usuario.email} - {usuario.iban} - Saldo: {usuario.saldo}")

    # 🔹 Formatar saldo no estilo correto europeu (21.200,00)
    saldo_numerico = float(usuario.saldo) if usuario.saldo else 0.0
    saldo_formatado = "{:,.2f}".format(saldo_numerico).replace(",", "X").replace(".", ",").replace("X", ".")

    # ✅ DEBUG: Verificar os dados antes de enviar para o template
    debug_dados = {
        "nome": usuario.nome,
        "email": usuario.email,
        "iban": usuario.iban,
        "saldo": saldo_formatado
    }
    print(f"✅ [DEBUG] Dados enviados para o template: {debug_dados}")

    return render_template(
        'dashboard.html',
        nome=usuario.nome,
        email=usuario.email,
        iban=usuario.iban,
        saldo=saldo_formatado
    )



    

@dashboard_bp.route("/api/historico_ordens", methods=["GET"])
def obter_historico_ordens():
    """Retorna todas as ordens fechadas do usuário logado"""
    try:
        session_db = Session()
        usuario_id = session.get("user_id")  # 🔥 Obtém o ID do usuário logado

        if not usuario_id:
            return jsonify({"erro": "Usuário não autenticado"}), 403

        # 🔥 Busca somente as ordens fechadas do usuário logado
        ordens_fechadas = session_db.query(Ordem).filter_by(usuario_id=usuario_id, status="fechada").all()
        session_db.close()

        return jsonify([
            {
                "id": ordem.id,
                "ativo": ordem.ativo,
                "preco_entrada": ordem.preco_entrada,
                "quantidade": ordem.quantidade,
                "tipo": ordem.tipo,
                "timestamp": ordem.timestamp.isoformat()
            }
            for ordem in ordens_fechadas
        ]), 200

    except Exception as e:
        print(f"⛔ Erro ao carregar histórico de ordens: {e}")
        return jsonify({"erro": "Erro interno no servidor"}), 500




@dashboard_bp.route("/api/ordens_abertas", methods=["GET"])
def obter_ordens_abertas():
    """Retorna apenas as ordens abertas do usuário logado"""
    session_db = Session()
    usuario_id = session.get("user_id")  # 🔥 Obtém o ID do usuário logado
    
    if not usuario_id:
        return jsonify({"erro": "Usuário não autenticado"}), 403

    # 🔥 Buscar somente as ordens do usuário logado
    ordens = session_db.query(Ordem).filter_by(usuario_id=usuario_id, status="aberta").all()
    session_db.close()

    return jsonify([
        {
            "id": ordem.id,
            "ativo": ordem.ativo,
            "preco_entrada": ordem.preco_entrada,
            "quantidade": ordem.quantidade,
            "tipo": ordem.tipo,  # ✅ Confirme que está sendo enviado corretamente
            "lucro_prejuizo": 0.0,  # 🔥 Placeholder temporário
            "timestamp": ordem.timestamp.isoformat()
        }
        for ordem in ordens
    ])
@dashboard_bp.route("/api/fechar_ordem/<int:ordem_id>", methods=["POST"])
def fechar_ordem(ordem_id):
    try:
        session_db = Session()
        ordem = session_db.query(Ordem).filter_by(id=ordem_id, status="aberta").first()

        if not ordem:
            session_db.close()
            return jsonify({"erro": "Ordem não encontrada ou já fechada"}), 404

        # 🔥 Aplicar comissão de 10%
        valor_ordem = ordem.preco_entrada * ordem.quantidade
        comissao = valor_ordem * 0.10  # 10% de comissão

        # 🔥 Buscar o usuário dono da ordem e debitar a comissão
        usuario = session_db.query(Usuario).filter_by(id=ordem.usuario_id).first()
        if usuario:
            usuario.saldo -= comissao  # 💰 Debita do saldo do usuário

        # 🔥 Atualizar status para fechada
        ordem.status = "fechada"
        ordem.comissao = comissao  # Armazena a comissão aplicada
        ordem.timestamp_fechamento = datetime.now(pytz.timezone("Europe/Lisbon"))  # ✅ Adiciona timestamp correto

        session_db.commit()
        session_db.close()

        return jsonify({"mensagem": "Ordem fechada com sucesso", "comissao": comissao}), 200

    except Exception as e:
        print(f"❌ Erro ao fechar ordem: {e}")
        return jsonify({"erro": "Erro interno no servidor"}), 500


@dashboard_bp.route("/api/order_book", methods=["GET"])
def obter_order_book():
    """Retorna todas as ordens abertas para exibição no livro de ordens"""
    session = Session()
    
    ordens_abertas = session.query(Ordem).filter_by(status="aberta").all()
    
    resultado = [
        {
            "id": ordem.id,
            "trader": session.query(Usuario).filter_by(id=ordem.usuario_id).first().nome,
            "quantidade": ordem.quantidade,
            "preco": ordem.preco_entrada,
            "data_hora": ordem.timestamp.isoformat(),
            "tipo": ordem.tipo  # ✅ 'buy' ou 'sell'
        }
        for ordem in ordens_abertas
    ]
    
    session.close()
    
    return jsonify(resultado), 200




