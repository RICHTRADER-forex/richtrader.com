from flask import Blueprint, jsonify
from services.market_engine import adjust_price  # ✅ CORRETO

market_bp = Blueprint('market', __name__)

@market_bp.route('/update_price', methods=['POST'])
def update_price():
    result = adjust_price()
    return jsonify(result)
