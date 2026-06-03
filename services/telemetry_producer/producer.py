import os
import time
import requests
from kafka import KafkaProducer

MBTA_URL = "https://cdn.mbta.com/realtime/VehiclePositions.pb"
KAFKA_TOPIC = "vehicle_positions"
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:29092")
API_KEY = os.getenv("MBTA_API_KEY")

def fetch_transit_data(url: str, api_key: str) -> bytes:
    headers = {"x-api-key": api_key} if api_key else {}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.content

def run_producer():
    producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)
    print(f"Starting producer connected to {KAFKA_BROKER}...")
    while True:
        try:
            data = fetch_transit_data(MBTA_URL, API_KEY)
            producer.send(KAFKA_TOPIC, data)
            producer.flush()
            print(f"[{time.strftime('%X')}] Sent {len(data)} bytes to {KAFKA_TOPIC}")
        except Exception as e:
            print(f"Error producing data: {e}")
        time.sleep(15)

if __name__ == "__main__":
    run_producer()
