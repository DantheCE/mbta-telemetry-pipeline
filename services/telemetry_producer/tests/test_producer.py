import pytest
import sys
import os

# Ensure the schemas directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

try:
    from schemas import gtfs_realtime_pb2
except ImportError:
    # Handle the case where the protobuf is not compiled yet
    gtfs_realtime_pb2 = None

@pytest.fixture
def mock_vehicle_position_payload():
    if not gtfs_realtime_pb2:
        pytest.skip("Protobuf classes not generated yet.")
        
    feed_message = gtfs_realtime_pb2.FeedMessage()
    
    header = feed_message.header
    header.gtfs_realtime_version = "2.0"
    header.incrementality = gtfs_realtime_pb2.FeedHeader.FULL_DATASET
    header.timestamp = 1627845600
    
    entity = feed_message.entity.add()
    entity.id = "vehicle_1"
    
    vehicle = entity.vehicle
    vehicle.trip.trip_id = "trip_a"
    vehicle.position.latitude = 42.3581
    vehicle.position.longitude = -71.0636
    vehicle.timestamp = 1627845600
    vehicle.vehicle.id = "v_123"
    
    return feed_message.SerializeToString()

def test_deserialize_vehicle_position(mock_vehicle_position_payload):
    """
    We are testing that the parsing function correctly takes a raw 
    binary Protobuf payload and successfully deserializes it into a 
    flat Python dictionary suitable for PostgreSQL insertion.
    """
    if not gtfs_realtime_pb2:
        pytest.skip("Protobuf classes not generated yet.")
        
    from telemetry_parser import parse_vehicle_positions
    
    result = parse_vehicle_positions(mock_vehicle_position_payload)
    
    assert len(result) == 1
    record = result[0]
    assert record["entity_id"] == "vehicle_1"
    assert record["trip_id"] == "trip_a"
    assert record["latitude"] == 42.3581
    assert record["longitude"] == -71.0636
    assert record["timestamp"] == 1627845600
    assert record["vehicle_id"] == "v_123"
