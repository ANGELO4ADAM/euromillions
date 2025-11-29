#!/usr/bin/env bash
set -e

# Start Flask API
python app_factory.py &
FLASK_PID=$!

# Start Celery worker if available
celery -A tasks.celery_app worker --loglevel=info &
CELERY_PID=$!

# Start Redis if present
if command -v redis-server >/dev/null 2>&1; then
  redis-server --port 6379 &
  REDIS_PID=$!
fi

echo "Flask PID: $FLASK_PID"
echo "Celery PID: $CELERY_PID"
if [ -n "$REDIS_PID" ]; then
  echo "Redis PID: $REDIS_PID"
fi
wait
