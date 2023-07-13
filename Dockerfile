# app/Dockerfile

FROM python:3.11-slim

EXPOSE 8501

WORKDIR /app

RUN apt-get update && apt-get install -y \
    pip3 install poetry \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN poetry install

ENTRYPOINT ["streamlit", "run", "utils/main.py", "--server.port=8501", "--server.address=0.0.0.0"]