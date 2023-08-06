# Dockerfile for embedding_api
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python -

WORKDIR /embedder

COPY pyproject.toml poetry.lock ./
RUN $HOME/.local/bin/poetry install --no-root --no-dev

COPY embedder/main.py .

EXPOSE 8532

CMD uvicorn main:app --host 0.0.0.0 --port 8532
