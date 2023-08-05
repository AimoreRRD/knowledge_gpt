from hashlib import md5
from typing import List
import requests

import streamlit as st
from langchain.docstore.document import Document
from langchain.vectorstores import VectorStore

def load_embedder(model_name):
    EMBEDDING_API_URL = f"http://0.0.0.0:8532/load_model/"

    data = {"model_name": model_name}
    headers = {"accept": "application/json"}

    response = requests.post(url=EMBEDDING_API_URL, params=data, headers=headers)

    if response.status_code == 200:
        return str(response.json())
    return None


def hash_func(doc: Document) -> str:
    """Hash function for caching Documents"""
    return md5(doc.page_content.encode("utf-8")).hexdigest()


@st.cache_data(show_spinner="Indexing document... This may take a while⏳", hash_funcs={Document: hash_func})
def embed_docs(docs: List[Document]) -> VectorStore:
    EMBEDDING_API_URL = "http://0.0.0.0:8532/embed/"

    # data = {"docs": docs}
    headers = {"accept": "application/json"}

    response = requests.post(url=EMBEDDING_API_URL, headers=headers, json=docs)

    if response.status_code == 200:
        return response.json()["index"]
    return None