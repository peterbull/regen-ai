FROM python:3.10.12-slim

ENV POETRY_VERSION=1.7.1
WORKDIR /usr/src/app

ENV PYTHONPATH /usr/src/app

COPY pyproject.toml poetry.lock ./
RUN apt-get update --fix-missing && \
    apt-get install --no-install-recommends -y gcc libc-dev libpq-dev

# RUN curl -fsSL https://ollama.com/install.sh | sh

RUN pip install "poetry==$POETRY_VERSION" && \
    poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

COPY . .
