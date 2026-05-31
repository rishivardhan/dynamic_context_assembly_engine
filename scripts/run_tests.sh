#!/usr/bin/env bash
# Run the unit test suite (no database required)
set -e
cd "$(dirname "$0")/.."

echo "Installing backend dependencies..."
cd backend && pip install -r requirements.txt -q && cd ..

echo "Running DCAE unit tests..."
pytest tests/ -v --tb=short

echo "Test run complete."
