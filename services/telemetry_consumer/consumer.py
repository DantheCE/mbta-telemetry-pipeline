import os
import psycopg2
from psycopg2.extras import execute_values
from kafka import KafkaConsumer
import sys

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
    
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id="transit_consumer_group",
        auto_offset_reset='earliest',
        security_protocol="SASL_SSL",
        sasl_mechanism="SCRAM-SHA-256",
        sasl_plain_username=KAFKA_USERNAME,
        sasl_plain_password=KAFKA_PASSWORD
    )
    
    print(f"Starting consumer connected to {KAFKA_BROKER}...")
    
    # Poll for messages, waiting up to 10 seconds. If no messages, it returns empty.
    messages_dict = consumer.poll(timeout_ms=10000)
    
    if not messages_dict:
        print("No new messages found in the topic. Exiting gracefully.")
        return
        
    total_inserted = 0
    for tp, messages in messages_dict.items():
        for message in messages:
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
                
                total_inserted += len(records)
            except Exception as e:
                print(f"Error consuming message: {e}")
                
    print(f"Batch processing complete. Inserted {total_inserted} records into Postgres.")


if __name__ == "__main__":
    run_consumer()
