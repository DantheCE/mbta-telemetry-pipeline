import os
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
