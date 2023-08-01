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

ARG POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /knowledge_gpt

COPY pyproject.toml poetry.lock ./
RUN touch README.md

COPY knowledge_gpt ./knowledge_gpt
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev

# FROM python:3.11-slim-buster as runtime

ENV VIRTUAL_ENV=/knowledge_gpt/.venv \
    PATH="/knowledge_gpt/.venv/bin:$PATH"

# COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health


ENTRYPOINT ["streamlit", "run", "knowledge_gpt/main.py", "--server.port=8501", "--server.address=0.0.0.0"]

#  ---------------------------

# ARG APP_NAME=knowledge_gpt
# ARG APP_PATH=/opt/$APP_NAME
# ARG PYTHON_VERSION=3.11.4
# ARG POETRY_VERSION=1.5.1

# ENV \
#     PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1 \
#     PYTHONFAULTHANDLER=1
# ENV \
#     POETRY_VERSION=$POETRY_VERSION \
#     POETRY_HOME="/opt/poetry" \
#     POETRY_VIRTUALENVS_IN_PROJECT=true \
#     POETRY_NO_INTERACTION=1

# RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python
# ENV PATH="$POETRY_HOME/bin:$PATH"

# WORKDIR $APP_PATH
# COPY ./poetry.lock ./pyproject.toml ./
# COPY ./$APP_NAME ./$APP_NAME

# FROM staging as development
# ARG APP_NAME
# ARG APP_PATH

# WORKDIR $APP_PATH
# RUN poetry install

# ENV FLASK_APP=$APP_NAME \
#     FLASK_ENV=development \
#     FLASK_RUN_HOST=0.0.0.0 \
#     FLASK_RUN_PORT=8888

# ENTRYPOINT ["poetry", "run"]
# CMD ["flask", "run"]


# FROM staging as build
# ARG APP_PATH

# WORKDIR $APP_PATH
# RUN poetry build --format wheel
# RUN poetry export --format requirements.txt --output constraints.txt --without-hashes


# FROM python:$PYTHON_VERSION as production
# ARG APP_NAME
# ARG APP_PATH

# ENV \
#     PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1 \
#     PYTHONFAULTHANDLER=1

# ENV \
#     PIP_NO_CACHE_DIR=off \
#     PIP_DISABLE_PIP_VERSION_CHECK=on \
#     PIP_DEFAULT_TIMEOUT=100

# WORKDIR $APP_PATH
# COPY --from=build $APP_PATH/dist/*.whl ./
# COPY --from=build $APP_PATH/constraints.txt ./
# RUN pip install ./$APP_NAME*.whl --constraint constraints.txt

# # gunicorn port. Naming is consistent with GCP Cloud Run
# ENV PORT=8888
# # export APP_NAME as environment variable for the CMD
# ENV APP_NAME=$APP_NAME

# COPY ./docker/docker-entrypoint.sh /docker-entrypoint.sh
# # CMD ["gunicorn", "--bind :$PORT", "--workers 1", "--threads 1", "--timeout 0", "\"$APP_NAME:create_app()\""] # 3
# ENTRYPOINT ["streamlit", "run", "knowledge_gpt/main.py", "--server.port=8501", "--server.address=0.0.0.0"]