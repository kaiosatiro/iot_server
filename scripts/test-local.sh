#! /usr/bin/env bash

docker compose down -v --remove-orphans 

if [ $(uname -s) = "Linux" ]; then
    echo "Remove __pycache__ files"
    sudo find . -type d -name __pycache__ -exec rm -r {} \+
fi

echo "TESTS | building..."
docker compose build
docker compose up -d

# Test the services
echo "TESTS | LOGGING"
docker compose exec -T logging bash tests-start.sh "$@"

echo "TEST | USERAPI"
docker compose exec -T userapi bash tests-start.sh "$@"

echo "TEST | RECEIVER"
docker compose exec -T receiver bash tests-start.sh "$@"

echo "TEST | HANDLER"
docker compose exec -T handler bash tests-start.sh "$@"

echo "TESTS | cleaning up..."
docker compose down -v --remove-orphans
