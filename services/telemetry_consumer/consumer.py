import os
import urllib.parse
import psycopg2
from psycopg2.extras import execute_values
from confluent_kafka import Consumer
import sys
import time

import gtfs_realtime_pb2

def parse_vehicle_positions(raw_bytes: bytes) -> list[dict]:
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(raw_bytes)
    records = []
    for entity in feed.entity:
        if entity.HasField('vehicle'):
            vehicle = entity.vehicle
            records.append({
                "entity_id": entity.id,
                "trip_id": vehicle.trip.trip_id,
                "latitude": vehicle.position.latitude,
                "longitude": vehicle.position.longitude,
                "timestamp": vehicle.timestamp,
                "vehicle_id": vehicle.vehicle.id
            })
    return records

KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "vehicle_positions")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:29092")
DB_DSN = os.getenv("DB_DSN", "postgresql://admin:password@localhost:5432/transit_db")
KAFKA_USERNAME = os.getenv("KAFKA_USERNAME")
KAFKA_PASSWORD = os.getenv("KAFKA_PASSWORD")

def get_db_connection(dsn: str):
    """
    Safely parse DSN to handle special characters (like '@') in the password
    that break standard URI parsers.
    """
    if not dsn:
        raise ValueError("DB_DSN is empty or not provided")
        
    # Strip whitespace and literal quotes which often happen during copy/paste to GitHub Secrets
    dsn = dsn.strip().strip('\'"').strip()
    
    # Sometimes platforms provide jdbc prefixes
    if dsn.startswith("jdbc:"):
        dsn = dsn[5:]
        
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
    conn = get_db_connection(DB_DSN)
    init_db(conn)
    
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'transit_consumer_group',
        'auto.offset.reset': 'earliest',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'SCRAM-SHA-256',
        'sasl.username': KAFKA_USERNAME,
        'sasl.password': KAFKA_PASSWORD,
        'enable.auto.commit': False
    })
    
    consumer.subscribe([KAFKA_TOPIC])
    print(f"Starting consumer connected to {KAFKA_BROKER} on topic {KAFKA_TOPIC}...")
    
    total_inserted = 0
    start_time = time.time()
    
    try:
        empty_polls = 0
        while True:
            # Enforce an absolute max runtime of 4 minutes so Cloud Run doesn't hang forever
            if time.time() - start_time > 240:
                print("Max execution time reached. Exiting.")
                break
                
            # Poll waits up to 2 seconds for a message
            msg = consumer.poll(timeout=2.0)
            
            if msg is None:
                empty_polls += 1
                if empty_polls >= 3:
                    # 6 seconds of absolutely no messages -> queue is empty
                    break
                continue
                
            empty_polls = 0
            
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
                
            records = parse_vehicle_positions(msg.value())
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
            
            total_inserted += len(records)
            
        # Commit the Kafka offsets only after successful DB insertion
        consumer.commit(asynchronous=False)
        print(f"Batch processing complete. Inserted {total_inserted} records into Postgres.")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        consumer.close()
        conn.close()

if __name__ == "__main__":
    run_consumer()
