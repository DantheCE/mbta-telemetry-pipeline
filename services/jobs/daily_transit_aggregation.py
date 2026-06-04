import os
import psycopg2
from datetime import date, timedelta

DB_DSN = os.getenv("DB_DSN")

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
    
    with psycopg2.connect(DB_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(create_table_sql)
            cur.execute(aggregate_sql, (target_date,))
            print(f"Aggregation completed for {target_date}. Rows affected: {cur.rowcount}")

if __name__ == "__main__":
    if not DB_DSN:
        raise ValueError("DB_DSN environment variable is required")
    run_aggregation()
