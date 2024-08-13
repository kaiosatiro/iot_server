FROM python:3.12.4-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.8.3

WORKDIR /app/

RUN pip install --no-cache-dir poetry

COPY ./pyproject.toml ./poetry.lock* /app/

ARG ENVIRONMENT
RUN bash -c "if [ $ENVIRONMENT == 'production' ] || [ $ENVIRONMENT == 'staging' ]; then poetry install --no-root --only main; else poetry install --no-root ; fi"

ENV PYTHONPATH=/app

COPY ./prestart.sh /app/

COPY . /app/

RUN chmod +x /app/prestart.sh

ENTRYPOINT ["./prestart.sh"]