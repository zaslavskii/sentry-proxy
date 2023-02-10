FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    POETRY_HOME='/home/poetry' \
    POETRY_VERSION=1.3.0 \
    PATH="/home/poetry/bin:$PATH"

WORKDIR /home/app

# install poetry
RUN apt update -y && \
    apt install curl make -y && (curl -sSL https://install.python-poetry.org | python -) && \
    poetry config virtualenvs.create false

# Copying configs of a project
COPY pyproject.toml poetry.lock /home/app/

# Installing dependencies
RUN poetry install --no-root --no-dev

FROM base AS test

# Installing dev dependencies
RUN poetry install --no-root

COPY Makefile /home/app/
COPY sentry_proxy /home/app/sentry_proxy
COPY tests /home/app/tests

# Installing app
RUN poetry install

FROM base AS prod

COPY sentry_proxy /home/app/sentry_proxy

# Installing app
RUN poetry install --no-dev

ENTRYPOINT ["proxy"]
EXPOSE 8899
