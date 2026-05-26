#!/bin/bash
set -e

# Only run migrations if we are starting the API server
if [ "$1" = "uvicorn" ]; then
    echo "Running Database Migrations..."
    alembic upgrade head
fi

echo "Starting: $@"
exec "$@"
