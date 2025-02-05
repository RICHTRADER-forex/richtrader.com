from flask import Blueprint, request, jsonify
from services.fees_manager import apply_fee  # ✅ CORRETO

fees_bp = Blueprint('fees', __name__)

@fees_bp.route('/apply_fee', methods=['POST'])
def apply_fee_route():
    data = request.json
    trader_id = data.get("trader_id")
    profit = data.get("profit")
    
    result = apply_fee(trader_id, profit)
    return jsonify(result)
