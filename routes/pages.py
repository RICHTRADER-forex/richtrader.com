from flask import Blueprint, render_template, session, redirect, url_for
from utils import login_required  # ✅ Importando o decorador de proteção

# Criando o Blueprint das páginas
pages_bp = Blueprint("pages", __name__)

# 🔹 Página inicial (home) - não precisa de login
@pages_bp.route("/")
def home():
    return render_template("home.html")

# 🔹 Página do dashboard (PROTEGIDA)
@pages_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# 🔹 Página de login
@pages_bp.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

# 🔹 Página de registro (cadastro)
@pages_bp.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")

# 🔹 Página de depósito (PROTEGIDA)
@pages_bp.route("/deposito", methods=["GET", "POST"])
@login_required
def deposito():
    return render_template("deposito.html")

# 🔹 Página de retirada (PROTEGIDA)
@pages_bp.route("/retirada", methods=["GET", "POST"])
@login_required
def retirada():
    return render_template("retirada.html")

# 🔹 Página de histórico (PROTEGIDA)
@pages_bp.route("/historico")
@login_required
def historico():
    return render_template("historico.html")

# 🔹 Página de ordens abertas (PROTEGIDA)
@pages_bp.route("/ordens_abertas")
@login_required
def ordens_abertas():
    return render_template("ordens_abertas.html")

# 🔹 Página do order book (PROTEGIDA)
@pages_bp.route("/order_book")
@login_required
def order_book():
    return render_template("order_book.html")

# 🔹 Página do gráfico (PROTEGIDA)
@pages_bp.route("/grafico")
@login_required
def grafico():
    return render_template("grafico.html")

# 🔹 🚀 Rota para Logout
@pages_bp.route("/logout")
def logout():
    session.pop("user_id", None)  # 🔥 Remove o usuário da sessão
    return redirect(url_for("pages.login"))  # ✅ Redireciona para login
