#! /usr/bin/env sh

# Exit in case of error
set -e
set -x

# Build in pre enviroment
docker compose build
docker compose down -v --remove-orphans # Remove possibly previous broken stacks left hanging after an error
docker compose up -d

# Run tests on each service
docker compose exec -T logging bash tests-start.sh "$@"
docker compose exec -T userapi bash tests-start.sh "$@"

# Clean up
docker compose down -v --remove-orphans
