#!/usr/bin/env bash
echo $PWD
echo $ENVIRONMENT
echo $RABBITMQ_DNS

# Let the DB start
python src/pre_start.py

# Start application
python src/main.py