#!/usr/bin/env bash
echo $PWD
echo $ENVIRONMENT
echo $LOG_LEVEL
echo $RABBITMQ_DNS

# Let the DB start
python src/backend_pre_start.py || exit 1

# Run migrations
# alembic upgrade head

# Create initial data in DB
python src/initial_data.py || exit 1

# Start application
if [ "$ENVIRONMENT" = "dev" ]; then
    fastapi dev src/main.py --host 0.0.0.0 --port 8000
else
    fastapi run src/main.py --port 8000
fi