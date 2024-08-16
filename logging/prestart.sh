#!/usr/bin/env bash
set -e
set -x

echo $PWD
echo $ENVIRONMENT
echo $LOG_LEVEL
echo $RABBITMQ_DNS
echo $LOG_INFO_LOCAL_PATH

# Let the DB start
python src/pre_start.py || exit 1

# Start application
python src/main.py
