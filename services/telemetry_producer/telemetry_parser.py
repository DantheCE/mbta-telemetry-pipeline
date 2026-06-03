from schemas import gtfs_realtime_pb2

def parse_vehicle_positions(raw_bytes: bytes) -> list[dict]:
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(raw_bytes)
    
    records = []
    for entity in feed.entity:
        if entity.HasField('vehicle'):
            vehicle = entity.vehicle
            records.append({
                "entity_id": entity.id,
                "trip_id": vehicle.trip.trip_id,
                "latitude": vehicle.position.latitude,
                "longitude": vehicle.position.longitude,
                "timestamp": vehicle.timestamp,
                "vehicle_id": vehicle.vehicle.id
            })
    return records
