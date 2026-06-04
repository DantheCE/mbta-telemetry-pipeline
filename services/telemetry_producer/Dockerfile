# Stage 1: Fetch and Compile Protobuf
FROM python:3.10-slim AS builder
RUN apt-get update && apt-get install -y curl protobuf-compiler
WORKDIR /build
# Fetch the official GTFS-Realtime schema
RUN curl -O https://raw.githubusercontent.com/google/transit/master/gtfs-realtime/proto/gtfs-realtime.proto
# Compile the Python classes
RUN protoc --python_out=. gtfs-realtime.proto

# Stage 2: Final Runtime Image
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Bring in the compiled schema from the builder stage
COPY --from=builder /build/gtfs_realtime_pb2.py .
CMD ["python", "producer.py"]
