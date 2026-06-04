import os
import time
import requests
from confluent_kafka import Producer

MBTA_URL = "https://cdn.mbta.com/realtime/VehiclePositions.pb"
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "vehicle_positions")
KAFKA_USERNAME = os.getenv("KAFKA_USERNAME")
KAFKA_PASSWORD = os.getenv("KAFKA_PASSWORD")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:29092")
API_KEY = os.getenv("MBTA_API_KEY")

def fetch_transit_data(url: str, api_key: str) -> bytes:
    headers = {"x-api-key": api_key} if api_key else {}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.content

def run_producer():
    producer = Producer({
        'bootstrap.servers': KAFKA_BROKER,
        'security.protocol': 'SASL_SSL',
        'sasl.mechanisms': 'SCRAM-SHA-256',
        'sasl.username': KAFKA_USERNAME,
        'sasl.password': KAFKA_PASSWORD,
    })
    
    print(f"Starting producer connected to {KAFKA_BROKER}...")
    try:
        data = fetch_transit_data(MBTA_URL, API_KEY)
        
        def delivery_callback(err, msg):
            if err:
                print(f"Message delivery failed: {err}")
            else:
                print(f"[{time.strftime('%X')}] Sent {len(msg.value())} bytes to {msg.topic()}")
                
        producer.produce(KAFKA_TOPIC, value=data, callback=delivery_callback)
        # Block until the message is sent
        producer.flush(10.0)
        
    except Exception as e:
        print(f"Error producing data: {e}")

if __name__ == "__main__":
    run_producer()
