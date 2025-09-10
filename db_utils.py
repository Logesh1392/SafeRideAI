import psycopg2

DB_CONFIG = {
    "host": "central-db.********.ap-south-1.rds.amazonaws.com",
    "dbname": "postgres",
    "user": "postgres",
    "password": "*********",
    "port": 5432
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)
