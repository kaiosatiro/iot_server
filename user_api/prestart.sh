#!/usr/bin/env bash
set -e
set -x

echo $PWD
echo $ENVIRONMENT
echo $LOG_LEVEL
echo $RABBITMQ_DNS

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
    fastapi run src/main.py --port 8000
fi