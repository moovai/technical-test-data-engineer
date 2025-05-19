#!/bin/bash
set -e

echo "Starting data pipeline..."

# Wait for FastAPI to be ready
echo "Waiting for FastAPI to be ready..."
until curl -s http://fastapi:8000/docs > /dev/null; do
    echo "Waiting for FastAPI..."
    sleep 2
done

# Run data extraction
echo "Extracting data..."
python3 src/moovitamix_fastapi/extract_data.py

# Run tests
echo "Running tests..."
PYTHONPATH=/app/src:/app/src/moovitamix_fastapi python3 -m pytest test/ -v

echo "Pipeline completed successfully!"