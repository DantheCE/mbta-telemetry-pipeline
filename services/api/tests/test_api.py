from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_metrics_endpoint():
    # It might fail with a 500 if DB is down, but we at least check that the route exists.
    # We will mock the DB connection to ensure it returns 200.
    from unittest.mock import patch
    with patch("main.get_db_connection") as mock_conn:
        mock_cursor = mock_conn.return_value.cursor.return_value.__enter__.return_value
        mock_cursor.fetchone.side_effect = [(100,), (5,), ("2023-01-01T00:00:00",)]
        
        response = client.get("/api/v1/metrics")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["total_records"] == 100
        assert data["active_vehicles_24h"] == 5
        assert data["last_updated"] == "2023-01-01T00:00:00"
