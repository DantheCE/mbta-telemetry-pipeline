# Project State & Architecture Handover

## Overview
This repository contains a **$0-cost Serverless Data Pipeline** for processing live MBTA (Boston Transit) GTFS-Realtime data. The project was originally guided by a local Docker-Compose/Kubernetes/Airflow architecture (as seen in `PROJECT_GUIDE.md`), but was aggressively refactored into a fully managed, serverless, and decoupled microservices architecture to stay completely within cloud free-tiers.

## Directory Structure
```text
pyKfAfProject/
├── .github/
│   └── workflows/
│       └── aggregation.yml              # GitHub Actions daily aggregation cron
├── services/
│   ├── telemetry_producer/
│   │   ├── Dockerfile                   # Multi-stage build for Protobuf
│   │   ├── requirements.txt
│   │   ├── producer.py                  # Fetches MBTA API & pushes to Redpanda
│   │   └── gtfs-realtime.proto
│   ├── telemetry_consumer/
│   │   ├── Dockerfile                   # Multi-stage build for Protobuf
│   │   ├── requirements.txt
│   │   ├── consumer.py                  # Consumes Redpanda & upserts to Postgres
│   │   └── gtfs-realtime.proto
│   ├── jobs/
│   │   └── daily_transit_aggregation.py # Python script for daily DB aggregation
│   └── airflow/                         # (Deprecated) Original local Airflow DAGs
├── create_topic.py                      # Script to provision Redpanda topics
├── PROJECT_GUIDE.md                     # Original architectural blueprint
└── PROJECT_STATE.md                     # Current LLM handover state
```

## Architecture Stack
* **Compute / Workers**: Google Cloud Run Jobs (Serverless) + Google Cloud Scheduler (Cron triggers)
* **Message Broker**: Redpanda Cloud Serverless (Kafka-compatible)
* **Database**: Supabase / Neon (Serverless PostgreSQL)
* **Orchestration / ETL**: GitHub Actions (Replaced Apache Airflow)
* **Data Serialization**: Protocol Buffers (Protobuf)

## Key Technical Decisions & Current State

### 1. Shift from Continuous Services to Batch Jobs
To achieve the $0-cost goal, the Python `producer.py` and `consumer.py` scripts were refactored. We stripped out all infinite `while True` loops and blocking network calls.
* **Producer**: Wakes up, makes exactly one HTTP request to the MBTA API, pushes binary Protobuf payloads to Redpanda, and terminates.
* **Consumer**: Uses `consumer.poll(timeout_ms=10000)` to consume all currently available messages in the Redpanda queue, parses them from binary Protobuf to Python dictionaries, performs a bulk `execute_values` `UPSERT` into Postgres (using `ON CONFLICT DO NOTHING`), and instantly terminates.
* **Execution**: Both are deployed as ephemeral **Google Cloud Run Jobs** triggered via HTTP POST from Google Cloud Scheduler every 5 minutes (offset by 1 minute).

### 2. Multi-Stage Docker Builds (Protobuf)
The GTFS-Realtime `.proto` file must be compiled into `gtfs_realtime_pb2.py` via `protoc`. To ensure clean deployments, we moved this compilation step entirely into a multi-stage `Dockerfile` for both the producer and consumer. The Python PB2 files are generated dynamically during the Docker build process and copied into the final runtime container. *(Note: Because they are generated at build-time, local IDEs may show a "module not found" linting error for `gtfs_realtime_pb2`, which is expected).*

### 3. Redpanda Serverless Specifics
* The topic `vehicle-positions` was created using a dedicated script (`create_topic.py`).
* **Critical Configuration**: Redpanda Cloud Serverless strictly requires a `replication_factor=3` for all topics. Also, due to the age of the `kafka-python` library, `api_version=(3, 3, 2)` was explicitly injected into the `KafkaAdminClient` to bypass `IncompatibleBrokerVersion` metadata request errors.
* **ACLs**: The `KAFKA_OPERATOR` user was explicitly granted "Allow" access to Consumer Groups (specifically `transit_consumer_group`) to bypass Kafka's strict `GroupAuthorizationFailedError`.

### 4. Airflow to GitHub Actions Migration
The daily aggregation logic (calculating average route delays and record counts from yesterday's data) was originally designed for Apache Airflow. Because Airflow requires a heavy, constantly running scheduler (which costs money), the logic was extracted into a pure Python/`psycopg2` script (`services/jobs/daily_transit_aggregation.py`).
* It executes raw SQL containing `INSERT ... ON CONFLICT DO UPDATE` to guarantee absolute idempotency.
* It is orchestrated via a stateless GitHub Actions cron runner (`.github/workflows/aggregation.yml`) executing daily at 02:00 UTC.

## Environment Variables (Injected via Secret Managers)
The following secrets are expected by the application. They are NOT stored in the Docker images; they are injected securely at runtime via Google Cloud Run's `--set-env-vars` flag and GitHub Actions Secrets:
* `KAFKA_BROKER`
* `KAFKA_USERNAME`
* `KAFKA_PASSWORD`
* `MBTA_API_KEY`
* `DB_DSN`

## Current Status
**PHASE 4 COMPLETED AND FULLY DEPLOYED.**
All infrastructure is provisioned. Docker images are securely stored in Google Artifact Registry (`us-central1`), Cloud Run Jobs are successfully processing data on a 5-minute schedule, and daily batch analytics are fully automated via GitHub Actions.
