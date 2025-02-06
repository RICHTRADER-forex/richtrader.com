import psycopg2

# Substitua pela sua URL do Render
DATABASE_URL = "postgres://seu_usuario:sua_senha@seu-banco.render.com:5432/seu_banco"

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Conexão com PostgreSQL bem-sucedida!")
    conn.close()
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
