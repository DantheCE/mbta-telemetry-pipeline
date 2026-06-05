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
