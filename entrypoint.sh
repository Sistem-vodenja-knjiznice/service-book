#!/bin/bash

APP_PORT=${PORT:-8001}

if [ "$RUN_CONSUMER" = "true" ]; then
  echo "Starting RabbitMQ consumer..."
  exec /opt/venv/bin/python /app/consumer.py
elif [ "$RUN_GRPC" = "true" ]; then
  echo "Starting gRPC server..."
  exec /opt/venv/bin/python /app/server.py
else
  echo "Starting Django application..."
  cd /app/
  exec /opt/venv/bin/gunicorn --worker-tmp-dir /dev/shm api.wsgi:application --bind "0.0.0.0:${APP_PORT}"
fi