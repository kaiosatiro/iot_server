#!/usr/bin/env bash
echo $PWD
echo $ENV
echo $RABBITMQ_DNS

# Let the DB start
python src/backend_pre_start.py

# Run migrations
# alembic upgrade head

# Create initial data in DB
python src/initial_data.py

# Start application
if [ "$ENV" = "dev" ]; then
    fastapi dev src/main.py --host 0.0.0.0 --port 8000
else
    fastapi run src/main.py --port 8000
fi