#! /usr/bin/env bash
set -e
set -x

python src/backend_pre_start.py || exit 1

# flake8 . --count --exit-zero --max-complexity=10 --max-line-length=150 --statistics --exclude=.venv
# flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=.venv

pytest
