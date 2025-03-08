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
RUN echo "INSTALL_DEV value: ${INSTALL_DEV}"
RUN if [ "${INSTALL_DEV}" = "true" ]; then \
        echo "Installing WITH dev dependencies" && \
        poetry install --no-root && \
        poetry show | grep ruff; \
    else \
        echo "Installing WITHOUT dev dependencies" && \
        poetry install --no-root --only main; \
    fi

ENV PYTHONPATH=/app

COPY ./Makefile ./
COPY ./opentariff/ ./opentariff/
COPY ./tests/ ./tests/

