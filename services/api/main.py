from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db import get_db_connection

app = FastAPI(title="MBTA Telemetry API")

# Allow CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/v1/vehicles/latest")
def get_latest_vehicles():
    """
    Returns the latest position for each active bus/vehicle.
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # We want the most recent row per entity_id
            # Using DISTINCT ON which is a Postgres feature
            query = """
                SELECT DISTINCT ON (entity_id) 
                    entity_id, trip_id, latitude, longitude, timestamp, vehicle_id 
                FROM vehicle_positions
                ORDER BY entity_id, timestamp DESC;
            """
            cur.execute(query)
            rows = cur.fetchall()
            
            # Format results
            results = []
            for row in rows:
                results.append({
                    "entity_id": row[0],
                    "trip_id": row[1],
                    "latitude": row[2],
                    "longitude": row[3],
                    "timestamp": row[4],
                    "vehicle_id": row[5]
                })
        conn.close()
        return {"data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/metrics")
def get_metrics():
    """
    Returns aggregate metrics and health telemetry for the dashboard.
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Total processed records
            cur.execute("SELECT COUNT(*) FROM vehicle_positions;")
            total_records = cur.fetchone()[0]
            
            # Active vehicles in the last 24 hours (86400 seconds)
            cur.execute("SELECT COUNT(DISTINCT vehicle_id) FROM vehicle_positions WHERE timestamp > (EXTRACT(EPOCH FROM NOW()) - 86400);")
            active_vehicles_24h = cur.fetchone()[0]
            
            # Last ingestion time
            cur.execute("SELECT MAX(created_at) FROM vehicle_positions;")
            last_updated = cur.fetchone()[0]

            # Ingestion rate (last 5 minutes)
            cur.execute("SELECT COUNT(*) FROM vehicle_positions WHERE created_at > NOW() - INTERVAL '5 minutes';")
            ingestion_rate_5m = cur.fetchone()[0]

            # Average pipeline latency (last 5 minutes)
            cur.execute("SELECT AVG(EXTRACT(EPOCH FROM created_at) - timestamp) FROM vehicle_positions WHERE created_at > NOW() - INTERVAL '5 minutes';")
            avg_latency = cur.fetchone()[0]
            
            # Consumer status
            cur.execute("SELECT (NOW() - MAX(created_at)) < INTERVAL '5 minutes' FROM vehicle_positions;")
            is_healthy = cur.fetchone()[0]
            consumer_status = "Healthy" if is_healthy else "Lagging" if last_updated else "Offline"
            
        conn.close()
        return {
            "data": {
                "total_records": total_records,
                "active_vehicles_24h": active_vehicles_24h,
                "last_updated": last_updated.isoformat() if last_updated else None,
                "ingestion_rate_5m": ingestion_rate_5m,
                "average_latency_seconds": round(avg_latency, 2) if avg_latency else 0.0,
                "consumer_status": consumer_status
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
