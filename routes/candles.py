from datetime import datetime, timedelta
import time
from threading import Thread
import pytz
from flask import Blueprint, request, jsonify, session, current_app
from database import Session, Candle, Ordem

candles_bp = Blueprint('candles', __name__)

# 🔥 Definir fuso horário de Lisboa
tz_lisboa = pytz.timezone("Europe/Lisbon")

# 🔹 Rota para gerar novas velas automaticamente a cada 5 minutos
@candles_bp.route("/api/grafico/atualizar", methods=["GET"])
def atualizar_grafico():
    session = Session()
    agora = datetime.now(tz_lisboa)

    ultima_vela = session.query(Candle).order_by(Candle.timestamp.desc()).first()
    ultima_timestamp = ultima_vela.timestamp if ultima_vela else agora - timedelta(minutes=5)

    if (agora - ultima_timestamp).total_seconds() >= 300:
        nova_vela = Candle(
            timestamp=agora,
            open=ultima_vela.close if ultima_vela else 100.0,
            high=ultima_vela.close if ultima_vela else 100.0,
            low=ultima_vela.close if ultima_vela else 100.0,
            close=ultima_vela.close if ultima_vela else 100.0,
            volume=0
        )
        session.add(nova_vela)
        session.commit()

        print(f"✅ Nova vela criada às {agora}")

        with current_app.app_context():
            socketio = current_app.extensions["socketio"]
            socketio.emit("nova_vela", {
                "time": nova_vela.timestamp.isoformat(),
                "open": nova_vela.open,
                "high": nova_vela.high,
                "low": nova_vela.low,
                "close": nova_vela.close,
                "volume": nova_vela.volume
            })

    session.close()
    return jsonify({"status": "ok"})

# 🔥 Atualizar vela ao processar ordens
@candles_bp.route("/api/grafico/ordem", methods=["POST"])
def processar_ordem():
    session = Session()
    data = request.json
    tipo = data.get("tipo")
    quantidade = float(data.get("quantidade", 0))
    preco_entrada = float(data.get("preco", 0))

    if not tipo or quantidade <= 0:
        return jsonify({"success": False, "message": "Dados inválidos!"}), 400

    ordem = Ordem(
        usuario_id=1,  
        ativo="EUR/USD",
        preco_entrada=preco_entrada,
        quantidade=quantidade,
        status="executada",
        tipo=tipo,
        timestamp=datetime.now()
    )
    session.add(ordem)
    session.commit()

    ultima_vela = session.query(Candle).order_by(Candle.timestamp.desc()).first()
    impacto = quantidade / 50000

    if ultima_vela:
        if tipo == "buy":
            ultima_vela.close += impacto * 10
            ultima_vela.high = max(ultima_vela.high, ultima_vela.close)
        elif tipo == "sell":
            ultima_vela.close -= impacto * 10
            ultima_vela.low = min(ultima_vela.low, ultima_vela.close)

        ultima_vela.volume += quantidade
        session.commit()

        with current_app.app_context():
            socketio = current_app.extensions["socketio"]
            socketio.emit("atualizar_vela", {
                "time": ultima_vela.timestamp.isoformat(),
                "open": ultima_vela.open,
                "high": ultima_vela.high,
                "low": ultima_vela.low,
                "close": ultima_vela.close,
                "volume": ultima_vela.volume
            })

    session.close()
    return jsonify({"success": True, "message": "Ordem processada com sucesso!"})

# 🔹 Obter a última vela
@candles_bp.route("/api/grafico/ultima-vela", methods=["GET"])
def obter_ultima_vela():
    session = Session()
    ultima_vela = session.query(Candle).order_by(Candle.timestamp.desc()).first()
    session.close()

    if not ultima_vela:
        return jsonify({"erro": "Nenhuma vela encontrada"}), 404

    return jsonify({
        "time": int(ultima_vela.timestamp.timestamp()),
        "open": ultima_vela.open,
        "high": ultima_vela.high,
        "low": ultima_vela.low,
        "close": ultima_vela.close,
        "volume": ultima_vela.volume
    })

# 🔹 Carregar o gráfico completo
@candles_bp.route("/api/grafico")
def carregar_grafico():
    session = Session()
    velas = session.query(Candle).order_by(Candle.timestamp).all()
    session.close()

    if not velas:
        return jsonify([])

    return jsonify([
        {
            "time": int(vela.timestamp.timestamp()),
            "open": vela.open,
            "high": vela.high,
            "low": vela.low,
            "close": vela.close,
            "volume": vela.volume
        }
        for vela in velas if None not in [vela.open, vela.high, vela.low, vela.close, vela.timestamp]
    ])

# 🔥 Função para atualizar velas automaticamente
def atualizar_velas_automaticamente():
    while True:
        try:
            session = Session()
            agora = datetime.now(tz_lisboa)
            ultima_vela = session.query(Candle).order_by(Candle.timestamp.desc()).first()

            if not ultima_vela:
                nova_vela = Candle(
                    timestamp=agora,
                    open=100.0, high=100.0, low=100.0, close=100.0, volume=0
                )
                session.add(nova_vela)
                session.commit()
            else:
                ultima_timestamp = ultima_vela.timestamp.replace(tzinfo=tz_lisboa)
                if (agora - ultima_timestamp).total_seconds() >= 300:
                    nova_vela = Candle(
                        timestamp=agora,
                        open=ultima_vela.close,
                        high=ultima_vela.close,
                        low=ultima_vela.close,
                        close=ultima_vela.close,
                        volume=0
                    )
                    session.add(nova_vela)
                    session.commit()

            session.close()
        except Exception as e:
            print(f"❌ Erro ao atualizar velas automaticamente: {e}")

        time.sleep(300)

# 🔥 Iniciar atualização automática apenas uma vez
if __name__ == "__main__":
    thread = Thread(target=atualizar_velas_automaticamente, daemon=True)
    thread.start()
