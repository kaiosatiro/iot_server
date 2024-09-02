#!/usr/bin/env bash
set -e
set -x

echo $PWD
echo $ENVIRONMENT
echo $LOG_LEVEL
echo $RABBITMQ_DNS
echo $INSERT_EXAMPLE_DATA

# Let the DB start
python src/backend_pre_start.py

# Run migrations
# alembic upgrade head

# Create initial data in DB
python src/initial_data.py

# Start application
if [ "$ENVIRONMENT" = "dev" ]; then
    fastapi dev src/main.py --host 0.0.0.0 --port 8000
else
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --forwarded-allow-ips='*' --proxy-headers
fi