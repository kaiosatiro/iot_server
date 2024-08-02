.PHONY: compose-dev compose-dev-d compose-down-dev compose-down clean-cache test-local lint

compose-prod:
	@echo "Starting production environment..."
	docker compose -f docker-compose.yml up --build -d

compose-dev-d:
	@echo "Starting development/test environment..."
	docker compose -f docker-compose.yml -f docker-compose-override.yml up --build -d

compose-dev:
	@echo "Starting development/test environment..."
	docker compose -f docker-compose.yml -f docker-compose-override.yml up --build

compose-down-dev:
	@echo "Stopping development/test environment..."
	docker compose down -v --remove-orphans

compose-down:
	@echo "Stopping development/test environment..."
	docker compose down --remove-orphans

clean-cache:
	@echo "Cleaning cache..."
	./scripts/clean-cache.sh

test-local: lint;
	@echo "Running tests..."
	./scripts/test-local.sh

lint:
	@echo "Running linteron Logging"
	flake8 logging/src --count --exit-zero --max-complexity=10 --max-line-length=150 --statistics --exclude=.venv
	flake8 logging/src --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=.venv

	@echo "Running linter on UserAPI"
	flake8 user_api/src --count --exit-zero --max-complexity=10 --max-line-length=150 --statistics --exclude=.venv
	flake8 user_api/src --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=.venv

