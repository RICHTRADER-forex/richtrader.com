import psycopg2

# Conexão com o banco PostgreSQL no Render
DATABASE_URL = "postgresql://rich_trader_db_user:D6YO4dNVH0EPjA8LA38qY59KrP4N5YfH@dpg-cui9oqbtq21c73cl0tog-a.oregon-postgres.render.com/rich_trader_db"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)
