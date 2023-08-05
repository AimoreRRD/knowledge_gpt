# Dockerfile for embedding_api
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python -

WORKDIR /llm

COPY pyproject.toml poetry.lock ./
RUN $HOME/.local/bin/poetry install --no-root --no-dev

COPY llm/main.py .

EXPOSE 8533

CMD uvicorn main:app --host 0.0.0.0 --port 8533
