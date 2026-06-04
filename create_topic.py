import os
from kafka.admin import KafkaAdminClient, NewTopic

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:29092")
KAFKA_TOPIC = "vehicle_positions"

def create_redpanda_topic():
    admin_client = KafkaAdminClient(
        bootstrap_servers=KAFKA_BROKER,
        security_protocol="SASL_SSL",
        sasl_mechanism="SCRAM-SHA-256",  # Update to match your Redpanda mechanism
        sasl_plain_username=os.getenv("KAFKA_USERNAME"),
        sasl_plain_password=os.getenv("KAFKA_PASSWORD"),
    )
    
    # 1 partition is sufficient for this project's throughput
    topic = NewTopic(name=KAFKA_TOPIC, num_partitions=1, replication_factor=1)
    
    try:
        admin_client.create_topics(new_topics=[topic], validate_only=False)
        print(f"Topic '{KAFKA_TOPIC}' created successfully.")
    except Exception as e:
        print(f"Failed to create topic: {e}")
    finally:
        admin_client.close()

if __name__ == "__main__":
    create_redpanda_topic()
