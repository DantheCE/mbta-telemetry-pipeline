import os
import urllib.parse
import psycopg2
from datetime import date, timedelta

DB_DSN = os.getenv("DB_DSN")

def get_db_connection(dsn: str):
    """
    Safely parse DSN to handle special characters (like '@') in the password
    that break standard URI parsers.
    """
    if not dsn:
        raise ValueError("DB_DSN is empty or not provided")
        
    if dsn.startswith("postgres://") or dsn.startswith("postgresql://"):
        scheme, rest = dsn.split("://", 1)
        if "/" in rest:
            auth_host, dbname = rest.rsplit("/", 1)
        else:
            auth_host, dbname = rest, ""
            
        if "@" in auth_host:
            auth, host_port = auth_host.rsplit("@", 1)
        else:
            auth, host_port = "", auth_host
            
        user_pass = auth.split(":", 1)
        user = user_pass[0] if len(user_pass) > 0 else ""
        password = user_pass[1] if len(user_pass) > 1 else ""
        
        host_port_split = host_port.split(":", 1)
        host = host_port_split[0] if len(host_port_split) > 0 else ""
        port = host_port_split[1] if len(host_port_split) > 1 else ""
        
        return psycopg2.connect(
            dbname=dbname,
            user=urllib.parse.unquote(user),
            password=urllib.parse.unquote(password),
            host=host,
            port=port
        )
    return psycopg2.connect(dsn)

def run_aggregation():
    target_date = date.today() - timedelta(days=1)
    
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS route_daily_stats (
            date_key DATE,
            trip_id VARCHAR(255),
            record_count INT,
            PRIMARY KEY (date_key, trip_id)
        );
    """
    
    aggregate_sql = """
        INSERT INTO route_daily_stats (date_key, trip_id, record_count)
        SELECT 
            DATE(TO_TIMESTAMP(timestamp)) as date_key,
            trip_id,
            COUNT(*) as record_count
        FROM vehicle_positions
        WHERE DATE(TO_TIMESTAMP(timestamp)) = %s
        GROUP BY 1, 2
        ON CONFLICT (date_key, trip_id) 
        DO UPDATE SET record_count = EXCLUDED.record_count;
    """
    
    with get_db_connection(DB_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(create_table_sql)
            cur.execute(aggregate_sql, (target_date,))
            print(f"Aggregation completed for {target_date}. Rows affected: {cur.rowcount}")

if __name__ == "__main__":
    if not DB_DSN:
        raise ValueError("DB_DSN environment variable is required")
    run_aggregation()
