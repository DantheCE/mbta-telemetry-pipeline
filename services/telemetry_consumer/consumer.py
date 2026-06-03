import os
import psycopg2
from psycopg2.extras import execute_values
from kafka import KafkaConsumer
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../telemetry_producer')))
from telemetry_parser import parse_vehicle_positions

KAFKA_TOPIC = "vehicle_positions"
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:29092")
DB_DSN = os.getenv("DB_DSN", "postgresql://admin:password@localhost:5432/transit_db")

def init_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vehicle_positions (
                entity_id VARCHAR(255),
                trip_id VARCHAR(255),
                latitude FLOAT,
                longitude FLOAT,
                timestamp BIGINT,
                vehicle_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (entity_id, timestamp)
            )
        """)
    conn.commit()

def run_consumer():
    conn = psycopg2.connect(DB_DSN)
    init_db(conn)
    
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id="transit_consumer_group",
        auto_offset_reset='earliest'
    )
    
    print(f"Starting consumer connected to {KAFKA_BROKER}...")
    
    for message in consumer:
        try:
            records = parse_vehicle_positions(message.value)
            if not records:
                continue
                
            insert_query = """
                INSERT INTO vehicle_positions (entity_id, trip_id, latitude, longitude, timestamp, vehicle_id)
                VALUES %s
                ON CONFLICT (entity_id, timestamp) DO NOTHING
            """
            values = [
                (r["entity_id"], r["trip_id"], r["latitude"], r["longitude"], r["timestamp"], r["vehicle_id"])
                for r in records
            ]
            
            with conn.cursor() as cur:
                execute_values(cur, insert_query, values)
            conn.commit()
            
            print(f"Inserted {len(records)} records into Postgres.")
        except Exception as e:
            print(f"Error consuming message: {e}")

if __name__ == "__main__":
    run_consumer()
