#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 5

# Run migrations
echo "Running database migrations..."
docker exec -i inventory_db psql -U kubo_user -d inventory_db < src/db/migrations.sql

echo "Migrations completed!"

