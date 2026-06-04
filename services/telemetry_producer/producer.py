import os
import time
import requests
from kafka import KafkaProducer

MBTA_URL = "https://cdn.mbta.com/realtime/VehiclePositions.pb"
KAFKA_TOPIC = "vehicle_positions"
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
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        security_protocol="SASL_SSL",
        sasl_mechanism="SCRAM-SHA-256",
        sasl_plain_username=KAFKA_USERNAME,
        sasl_plain_password=KAFKA_PASSWORD,
        api_version=(3, 3, 2)
    )
    print(f"Starting producer connected to {KAFKA_BROKER}...")
    try:
        data = fetch_transit_data(MBTA_URL, API_KEY)
        producer.send(KAFKA_TOPIC, data)
        producer.flush()
        print(f"[{time.strftime('%X')}] Sent {len(data)} bytes to {KAFKA_TOPIC}")
    except Exception as e:
        print(f"Error producing data: {e}")

if __name__ == "__main__":
    run_producer()
