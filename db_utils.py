import psycopg2
import pandas as pd

DB_CONFIG = {
    "host": "central-db.cd0e48gcg56c.ap-south-1.rds.amazonaws.com",
    "dbname": "postgres",
    "user": "postgres",
    "password": "Aug300825",   # ⚠️ move this to env variable later
    "port": 5432
}

def get_db_connection():
    """Create and return a PostgreSQL connection"""
    return psycopg2.connect(**DB_CONFIG)

def fetch_data(query):
    """Run a SELECT query and return result as pandas DataFrame"""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"⚠️ Database error: {e}")
        return pd.DataFrame()
