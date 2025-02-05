from flask import Blueprint, request, jsonify
from services.trader_manager import add_trader, remove_trader  # ✅ CORRETO

traders_bp = Blueprint('traders', __name__)

@traders_bp.route('/enter', methods=['POST'])
def enter_market():
    data = request.json
    trader_id = data.get("trader_id")
    balance = data.get("balance")
    
    result = add_trader(trader_id, balance)
    return jsonify(result)

@traders_bp.route('/exit', methods=['POST'])
def exit_market():
    data = request.json
    trader_id = data.get("trader_id")
    
    result = remove_trader(trader_id)
    return jsonify(result)
