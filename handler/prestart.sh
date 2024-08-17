#!/usr/bin/env bash
set -e
set -x

echo $PWD
echo $ENVIRONMENT
echo $LOG_LEVEL
echo $RABBITMQ_DNS
# echo $DB

# Let the DB start
python src/pre_start.py

# Start application
python src/main.py
