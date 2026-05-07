#!/bin/bash
set -e

echo "Running database migrations..."
cd /app/backend
alembic upgrade head

echo "Database migrations completed successfully!"
