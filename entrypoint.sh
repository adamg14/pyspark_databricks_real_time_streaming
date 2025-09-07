#!/bin/bash
# docker/entrypoint.sh
set -e

echo "Starting Spark component: $@"

# Wait for Spark master to be ready
if [[ "$1" == *"spark-class"* ]]; then
    echo "Waiting for Spark components to be ready..."
    sleep 10
fi

exec "$@"