# 📂 /Users/programacao/Documents/rich_trader_forex/fees_manager.py

from database import Session, Ordem

def apply_fee(order_id, percentage=0.10):
    """Aplica uma taxa sobre uma ordem fechada."""
    session = Session()
    ordem = session.query(Ordem).filter_by(id=order_id, status="fechada").first()

    if not ordem:
        session.close()
        return {"error": "Ordem não encontrada ou já processada"}

    fee = ordem.preco_entrada * ordem.quantidade * percentage
    ordem.comissao = fee
    session.commit()
    session.close()

    return {"success": True, "message": f"Taxa de {fee:.2f} aplicada na ordem {order_id}"}
