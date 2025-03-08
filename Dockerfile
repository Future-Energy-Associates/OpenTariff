FROM python:3.11-slim

WORKDIR /app

RUN apt-get update
RUN apt-get install -y curl make && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock README.md ./

ARG INSTALL_DEV=false
RUN bash -c "if [ \"$INSTALL_DEV\" = \"true\" ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

ENV PYTHONPATH=/app

COPY ./Makefile ./
COPY ./opentariff/ ./opentariff/
COPY ./tests/ ./tests/

