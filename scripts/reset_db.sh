#!/usr/bin/env bash
# Reset and re-seed the database (useful during development)
set -e

echo "Stopping containers..."
docker compose down -v

echo "Starting fresh..."
docker compose up -d postgres neo4j

echo "Waiting for databases to be ready..."
sleep 15

echo "Starting backend (will auto-init and seed)..."
docker compose up -d backend frontend

echo "Done. Access:"
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo "  Neo4j:     http://localhost:7474"
