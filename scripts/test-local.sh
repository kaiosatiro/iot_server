#! /usr/bin/env bash

set -e

docker compose down -v --remove-orphans 

if [ $(uname -s) = "Linux" ]; then
    echo "Remove __pycache__ files"
    sudo find . -type d -name __pycache__ -exec rm -r {} \+
fi

docker compose build
docker compose up -d
# Test the services
docker compose exec -T logging bash tests-start.sh "$@"
docker compose exec -T userapi bash tests-start.sh "$@"
docker compose exec -T receiver bash tests-start.sh "$@"
docker compose exec -T handler bash tests-start.sh "$@"

