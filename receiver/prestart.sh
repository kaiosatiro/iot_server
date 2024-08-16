#!/usr/bin/env bash
echo $PWD
echo $ENVIRONMENT
echo $LOG_LEVEL
echo $RABBITMQ_DNS

# Let the DB start

python src/pre_start.py || exit 1

# Start application
if [ "$ENVIRONMENT" = "dev" ]; then
    fastapi dev src/main.py --host 0.0.0.0 --port 8000
else
    fastapi run src/main.py --port 8000
fi