#!/bin/bash
set -e

echo "Seeding database with initial data..."
cd /app/backend
python -m scripts.seed_data

echo "Database seeding completed successfully!"
