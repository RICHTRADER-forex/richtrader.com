from config_db import get_db_connection

def criar_tabela():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        iban VARCHAR(22) UNIQUE NOT NULL,
        confirmado BOOLEAN DEFAULT FALSE,
        codigo_confirmacao TEXT NOT NULL
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tabela 'usuarios' criada com sucesso!")

if __name__ == "__main__":
    criar_tabela()
