.PHONY: install #migrations migrate run superuser update test install-pre-commit lint
install:
	@echo "Installing dependencies..."
	poetry install

# install-pre-commit:
# 	@echo "Installing pre-commit..."
# 	poetry run pre-commit uninstall; poetry run pre-commit install

# lint:
# 	@echo "Running linter(pre-commit)..."
# 	poetry run pre-commit run --all-files

# migrations:
# 	@echo "Creating migrations..."

# migrate:
# 	@echo "Running migrations..."

# run:
# 	@echo "Running server..."

# superuser:
# 	@echo "Creating superuser..."

# up-dependencies-only:
# 	@echo "Starting dependencies..."
# 	test -f .env || touch .env
# 	docker compose -f docker-compose.dev.yml up --force-recreate db

# update: install migrate install-pre-commit;

test:
	@echo "Running tests..."
	poetry run python -m pytest
