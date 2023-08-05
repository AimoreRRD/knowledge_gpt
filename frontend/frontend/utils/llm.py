from typing import Any, Dict, List

import streamlit as st
from langchain.docstore.document import Document
import requests


@st.cache_resource
def load_llm(model_name):
    LLM_API_URL = f"http://answering:8532/load_model/"

    data = {"model_name": model_name}
    headers = {"accept": "application/json"}

    response = requests.post(url=LLM_API_URL, params=data, headers=headers)

    if response.status_code == 200:
        return response.json()["index"]
    return None


# @st.cache_data(show_spinner=False, hash_funcs={Document: hash_func})
def get_answer(docs: List[Document], query: str) -> Dict[str, Any]:
    pass
