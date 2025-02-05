from flask import Blueprint, request, jsonify, session
from database import Session, Ordem

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/buy', methods=['POST'])
def buy():
    data = request.json
    trader_id = session.get("user_id")
    volume = data.get("volume")

    if not trader_id or not volume:
        return jsonify({"error": "Dados inválidos!"}), 400

    ordem = Ordem(usuario_id=trader_id, tipo="buy", quantidade=volume)
    session_db = Session()
    session_db.add(ordem)
    session_db.commit()
    session_db.close()

    return jsonify({"message": "Compra realizada com sucesso!"})

@orders_bp.route('/sell', methods=['POST'])
def sell():
    data = request.json
    trader_id = session.get("user_id")
    volume = data.get("volume")

    if not trader_id or not volume:
        return jsonify({"error": "Dados inválidos!"}), 400

    ordem = Ordem(usuario_id=trader_id, tipo="sell", quantidade=volume)
    session_db = Session()
    session_db.add(ordem)
    session_db.commit()
    session_db.close()

    return jsonify({"message": "Venda realizada com sucesso!"})
