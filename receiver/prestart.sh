#!/usr/bin/env bash
echo $PWD
echo $ENVIRONMENT
echo $RABBITMQ_DNS

# Let the DB start
# python src/backend_pre_start.py

# Start application
if [ "$ENVIRONMENT" = "dev" ]; then
    fastapi dev src/main.py --host 0.0.0.0 --port 8000
else
    fastapi run src/main.py --port 8000
fi