import urllib.request
import sys
sys.path.append('services/telemetry_consumer')
import gtfs_realtime_pb2
try:
    resp = urllib.request.urlopen('https://cdn.mbta.com/realtime/VehiclePositions.pb')
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(resp.read())
    for i, entity in enumerate(feed.entity[:3]):
        print(entity)
except Exception as e:
    print('Error:', e)
