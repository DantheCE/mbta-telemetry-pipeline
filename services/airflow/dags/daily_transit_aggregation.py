from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'daily_transit_aggregation',
    default_args=default_args,
    description='Aggregates yesterday transit stats',
    schedule_interval='@daily',
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    create_table = PostgresOperator(
        task_id='create_reporting_table',
        postgres_conn_id='postgres_default',
        sql="""
            CREATE TABLE IF NOT EXISTS route_daily_stats (
                date_key DATE,
                trip_id VARCHAR(255),
                record_count INT,
                PRIMARY KEY (date_key, trip_id)
            );
        """,
    )

    # Note the ON CONFLICT DO UPDATE for idempotency
    aggregate_delays = PostgresOperator(
        task_id='aggregate_delays',
        postgres_conn_id='postgres_default',
        sql="""
            INSERT INTO route_daily_stats (date_key, trip_id, record_count)
            SELECT 
                DATE(TO_TIMESTAMP(timestamp)) as date_key,
                trip_id,
                COUNT(*) as record_count
            FROM vehicle_positions
            WHERE DATE(TO_TIMESTAMP(timestamp)) = '{{ ds }}'::DATE
            GROUP BY 1, 2
            ON CONFLICT (date_key, trip_id) 
            DO UPDATE SET record_count = EXCLUDED.record_count;
        """,
    )

    create_table >> aggregate_delays
