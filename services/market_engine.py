# 📂 /Users/programacao/Documents/rich_trader_forex/services/market_engine.py

def adjust_price(orders):
    """Ajusta o preço do ativo com base nas ordens."""
    if not orders or len(orders) < 2:
        return None  # O preço só muda quando há pelo menos 2 ordens

    total_volume = sum(order['volume'] for order in orders)
    
    # Regra do mercado para ajustar o preço
    if orders[0]['type'] == 'buy' and orders[1]['type'] == 'buy':
        new_price = orders[0]['price'] * 1.0001  # Sobe 0.01%
    elif orders[0]['type'] == 'sell' and orders[1]['type'] == 'sell':
        new_price = orders[0]['price'] * 0.9999  # Cai 0.01%
    else:
        new_price = orders[0]['price']  # Se não houver padrão, mantém o preço

    return new_price
