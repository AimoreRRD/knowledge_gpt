# Dockerfile for frontend
FROM python:3.11.4

WORKDIR /knowledge_gpt

RUN apt-get update \
    && apt-get install -y build-essential python3-dev libblas3 liblapack3 liblapack-dev libblas-dev gfortran

RUN pip install --upgrade pip

COPY . /knowledge_gpt

RUN pip install -r requirements.txt

EXPOSE 8531

CMD streamlit run knowledge_gpt/streamlit_app.py --server.port 8531