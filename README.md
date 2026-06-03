# Scalable Transit Telemetry Pipeline (pyKfAfProject)

A robust, real-time data engineering pipeline designed to ingest, process, and persist high-velocity transit telemetry data. This project demonstrates proficiency in distributed systems, stream processing, and containerized infrastructure.

## Overview

The system continuously polls the Massachusetts Bay Transportation Authority (MBTA) API for live, GTFS-Realtime vehicle position data. Rather than processing and storing this data in a monolithic fashion, the pipeline leverages an event-driven architecture. Data is ingested, serialized, and published to Apache Kafka, allowing independent consumer microservices to process and persist the data into a PostgreSQL database asynchronously.

## Technology Stack

*   **Languages:** Python 3.10+
*   **Message Broker:** Apache Kafka, Zookeeper
*   **Database:** PostgreSQL
*   **Infrastructure:** Docker, Docker Compose
*   **Data Serialization:** Protocol Buffers (Protobuf)
*   **Testing:** Pytest (TDD methodology)

---

## Architecture

The application is decoupled into distinct, independently scalable services:

1.  **Telemetry Producer (`services/telemetry_producer`)**:
    *   Acts as the ingestion layer.
    *   Polls external APIs for binary Protobuf data.
    *   Publishes raw byte streams to the `vehicle_positions` Kafka topic.
2.  **Apache Kafka Cluster**:
    *   Serves as the high-throughput, fault-tolerant nervous system of the application.
    *   Decouples the ingestion of data from the processing of data.
3.  **Telemetry Consumer (`services/telemetry_consumer`)**:
    *   Subscribes to the Kafka topic.
    *   Deserializes the Protobuf payloads and applies business logic/transformations.
    *   Persists the structured data into PostgreSQL.
4.  **PostgreSQL Database**:
    *   Provides persistent, relational storage for historical telemetry analysis.

---

## Architectural Decisions & Trade-offs

Building a distributed system requires balancing complexity with scalability. Below are key design decisions made during development:

### 1. Apache Kafka vs. Direct Database Inserts
*   **Decision**: Introduced Apache Kafka as a middleware broker rather than having the producer write directly to PostgreSQL.
*   **Trade-off**: Increases operational complexity (requires maintaining Kafka/Zookeeper nodes) and infrastructure footprint.
*   **Justification**: Transit telemetry data can experience massive volume spikes. Kafka acts as a shock absorber. If the database goes down or consumer processing slows, Kafka buffers the messages, guaranteeing zero data loss. Furthermore, it allows multiple different consumer applications (e.g., an analytics engine and a live dashboard) to subscribe to the same data stream simultaneously without modifying the producer.

### 2. Protocol Buffers (Protobuf) vs. JSON
*   **Decision**: Utilized the GTFS-Realtime Protobuf specification over standard JSON payloads.
*   **Trade-off**: Protobufs are binary and not human-readable, making debugging slightly more difficult. They also require a compilation step to generate Python classes.
*   **Justification**: Protobufs offer strict, contract-based typing and are significantly smaller and faster to serialize/deserialize than JSON. This reduces network bandwidth and storage costs at scale.

### 3. Microservices vs. Monolith
*   **Decision**: Split the producer and consumer into entirely separate services running their own processes.
*   **Trade-off**: Code sharing is slightly harder, and running the application requires managing multiple processes via Docker Compose.
*   **Justification**: Independent deployability and scalability. If data ingestion is lightweight but data processing/database writes become a bottleneck, we can horizontally scale the consumer services independently of the producer.

### 4. Test-Driven Development (TDD)
*   **Decision**: Enforced strict TDD. Tests and mock payloads (fixtures) are written before business logic.
*   **Justification**: Ensures high code coverage, self-documenting code, and confidence when refactoring. It proves the system works deterministically before it ever touches the live Kafka cluster.

---

## Local Development Setup

To run this project locally, ensure you have **Docker** and **Docker Compose** installed.

### 1. Start the Infrastructure
Spin up the isolated Kafka, Zookeeper, and PostgreSQL containers:
```bash
docker-compose up -d
```

### 2. Configure Environment
Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # Or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Run the Pipeline
In one terminal instance, start the ingestion layer:
```bash
python services/telemetry_producer/producer.py
```

In a separate terminal instance, start the processing layer:
```bash
python services/telemetry_consumer/consumer.py
```

## Testing

This repository uses `pytest` for unit and integration testing. Mock Protobuf payloads are utilized to simulate API responses without requiring network calls.

```bash
# Run the entire test suite
pytest
```
