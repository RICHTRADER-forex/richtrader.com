from flask import Blueprint, render_template
from utils import login_required  # ✅ Importando a proteção de login

grafico_bp = Blueprint('grafico', __name__)  # ✅ Criando um Blueprint separado

@grafico_bp.route("/grafico")  # ✅ Criando a rota corretamente
@login_required  # 🔐 Protegendo o acesso à página
def grafico():
    return render_template("grafico.html")  # ✅ Renderizando o template correto
