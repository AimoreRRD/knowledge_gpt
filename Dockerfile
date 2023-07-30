# app/Dockerfile

# FROM python:3.11-slim

# EXPOSE 8501

# WORKDIR /app

# RUN apt-get update && apt-get install -y \
#     pip3 install poetry \
#     build-essential \
#     git \
#     && rm -rf /var/lib/apt/lists/*

# COPY . .

# RUN poetry install

# ENTRYPOINT ["streamlit", "run", "knowledge_gpt/main.py", "--server.port=8501", "--server.address=0.0.0.0"]

#  ---------------------------

# FROM python:3.11-slim-buster

# RUN pip install poetry==1.5.1

# ENV POETRY_NO_INTERACTION=1 \
#     POETRY_VIRTUALENVS_IN_PROJECT=1 \
#     POETRY_VIRTUALENVS_CREATE=1 \
#     POETRY_CACHE_DIR=/tmp/poetry_cache

# WORKDIR /app

# FROM python:3.11-slim-buster

# COPY pyproject.toml poetry.lock ./
# RUN touch README.md

# RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# COPY knowledge_gpt ./knowledge_gpt

# RUN poetry install --without dev

# ENTRYPOINT ["poetry", "run", "streamlit", "run", "knowledge_gpt.main.py"]

#  ---------------------------

FROM python:3.11-buster as builder

RUN pip install poetry==1.5.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /knowledge_gpt

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

FROM python:3.11-slim-buster as runtime

ENV VIRTUAL_ENV=/knowledge_gpt/.venv \
    PATH="/knowledge_gpt/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY knowledge_gpt ./knowledge_gpt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health


ENTRYPOINT ["streamlit", "run", "knowledge_gpt/main.py", "--server.port=8501", "--server.address=0.0.0.0"]