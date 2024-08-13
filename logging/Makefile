.PHONY: install run tests lint # install-pre-commit

install:
	@echo "Installing dependencies..."
	poetry install

# install-pre-commit:
# 	@echo "Installing pre-commit..."
# 	poetry run pre-commit uninstall; poetry run pre-commit install

lint:
	@echo "Running linter"
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=150 --statistics --exclude=.venv
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=.venv

	# mypy src
	# ruff check src --fix
	# ruff format src --check

run:
	@echo "Running server..."
	poetry run python src/main.py

# update: install install-pre-commit;

tests:
	@echo "Running tests..."
	poetry run python -m pytest

# poetry run pytest --lf tests/api/test_message.py -W ignore::DeprecationWarning
