# Dockerfile for frontend
FROM python:3.11.4

WORKDIR /frontend

RUN apt-get update \
    && apt-get install -y build-essential python3-dev libblas3 liblapack3 liblapack-dev libblas-dev gfortran

RUN pip install --upgrade pip 

COPY . /frontend

RUN pip install -r requirements.txt

EXPOSE 8531

CMD streamlit run frontend/main.py --server.port 8531