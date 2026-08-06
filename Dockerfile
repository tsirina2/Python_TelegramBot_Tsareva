FROM python:3.14

COPY pyproject.toml poetry.lock .

RUN pip install poetry && poetry install --only main --no-root --no-directory

COPY app/ ./app
COPY settings/ ./settings