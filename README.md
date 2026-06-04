# Scalable Transit Telemetry Pipeline (pyKfAfProject)

A robust, real-time data engineering pipeline designed to ingest, process, and persist high-velocity transit telemetry data. This project has been migrated from a local Docker-Compose setup to a fully managed, $0-cost Serverless cloud architecture.

## Overview

The system fetches live, GTFS-Realtime vehicle position data from the Massachusetts Bay Transportation Authority (MBTA) API. Rather than processing and storing this data in a monolithic fashion, the pipeline leverages an event-driven microservices architecture. Data is ingested, serialized into Protocol Buffers (Protobuf), and published to Redpanda (Kafka-compatible). Independent consumer jobs then drain the queue, deserialize the data, and persist it into a serverless PostgreSQL database (Supabase/Neon).

## Technology Stack

*   **Languages:** Python 3.10+
*   **Compute:** Google Cloud Run Jobs (Serverless) + Google Cloud Scheduler
*   **Message Broker:** Redpanda Cloud Serverless
*   **Database:** Supabase / Neon (Serverless PostgreSQL)
*   **Orchestration / ETL:** GitHub Actions
*   **Data Serialization:** Protocol Buffers (Protobuf)
*   **Containerization:** Docker (Multi-stage builds)

---

## Architecture

The application is decoupled into distinct, independently scalable services:

1.  **Telemetry Producer (`services/telemetry_producer`)**:
    *   Acts as the ingestion layer.
    *   Wakes up on a 5-minute schedule via Google Cloud Scheduler.
    *   Fetches the external MBTA API for binary Protobuf data and publishes to Redpanda.
2.  **Redpanda Cloud**:
    *   Serves as the high-throughput serverless message broker.
    *   Decouples the ingestion of data from the processing of data.
3.  **Telemetry Consumer (`services/telemetry_consumer`)**:
    *   Wakes up exactly 1 minute after the Producer.
    *   Drains the Redpanda queue and deserializes the Protobuf payloads.
    *   Executes bulk idempotent UPSERTs into PostgreSQL and gracefully exits.
4.  **Daily Aggregation Job (`services/jobs`)**:
    *   A stateless Python ETL script orchestrated via GitHub Actions cron.
    *   Calculates daily route metrics directly in Postgres.

---

## Future Roadmap: Frontend Dashboard

Currently, the pipeline acts as a robust backend engine. **The immediate next step in the roadmap is to build a responsive frontend dashboard.** 

This dashboard will connect to the Supabase database to visualize the MBTA data in a meaningful way, allowing users to track real-time transit telemetry, vehicle delays, and historical route aggregations through interactive maps and charts.

## Deployment & Setup

The infrastructure relies on Google Cloud Run and GitHub Actions. See `PROJECT_STATE.md` for a comprehensive handover document outlining the specific architectural configurations, environment variables, and deployment intricacies.
