import sys
import os
from fastapi.testclient import TestClient
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

client = TestClient(app)

def test_eval_get_latest_vehicles():
    # We mock the DB connection to ensure the endpoint logic processes data correctly without a live DB
    with patch("main.get_db_connection") as mock_conn:
        mock_cursor = mock_conn.return_value.cursor.return_value.__enter__.return_value
        mock_cursor.fetchall.return_value = [
            ("y1234", "trip_1", 42.3601, -71.0589, 1620000000, "veh_1")
        ]
        
        response = client.get("/api/v1/vehicles/latest")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["entity_id"] == "y1234"
        assert data[0]["latitude"] == 42.3601

if __name__ == "__main__":
    print("Running API Eval...")
    test_eval_get_latest_vehicles()
    test_eval_metrics()
    print("API Eval passed!")

def test_eval_metrics():
    with patch("main.get_db_connection") as mock_conn:
        mock_cursor = mock_conn.return_value.cursor.return_value.__enter__.return_value
        mock_cursor.fetchone.side_effect = [(500,), (15,), ("2023-01-01T00:00:00",)]
        
        response = client.get("/api/v1/metrics")
        assert response.status_code == 200
        data = response.json()["data"]
        
        assert "total_records" in data
        assert "active_vehicles_24h" in data
        assert "last_updated" in data
        assert isinstance(data["total_records"], int)
        assert isinstance(data["active_vehicles_24h"], int)
        assert isinstance(data["last_updated"], str)
