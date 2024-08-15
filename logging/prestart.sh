#!/usr/bin/env bash
echo $PWD
echo $ENVIRONMENT
echo $RABBITMQ_DNS
echo $LOG_INFO_LOCAL_PATH

# Let the DB start
python src/pre_start.py || exit 1

# Start application
python src/main.py
