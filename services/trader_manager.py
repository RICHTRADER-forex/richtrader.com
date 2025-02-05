# 📂 /Users/programacao/Documents/rich_trader_forex/services/trader_manager.py

from database import Session, Usuario

def add_trader(trader_id, balance):
    """Adiciona um novo trader ao mercado"""
    session = Session()
    trader = session.query(Usuario).filter_by(id=trader_id).first()

    if not trader:
        session.close()
        return {"error": "Trader não encontrado"}

    trader.saldo += balance
    session.commit()
    session.close()
    return {"success": True, "message": f"Trader {trader_id} entrou no mercado com {balance} saldo"}

def remove_trader(trader_id):
    """Remove um trader do mercado"""
    session = Session()
    trader = session.query(Usuario).filter_by(id=trader_id).first()

    if not trader:
        session.close()
        return {"error": "Trader não encontrado"}

    session.delete(trader)
    session.commit()
    session.close()
    return {"success": True, "message": f"Trader {trader_id} saiu do mercado"}
