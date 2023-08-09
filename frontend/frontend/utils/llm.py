from typing import Any, Dict, List

import requests
import streamlit as st


@st.cache_resource
def load_llm(model_name):
    LLM_API_URL = "http://answering:8533/load_model/"

    data = {"model_name": model_name}
    headers = {"accept": "application/json"}

    response = requests.post(url=LLM_API_URL, params=data, headers=headers)

    if response.status_code == 200:
        return response.json()["index"]
    return None


# @st.cache_data(show_spinner=False, hash_funcs={Document: hash_func})
def get_answer(query: str, documents_selected: List[str]) -> Dict[str, Any]:
    LLM_API_URL = "http://answering:8533/get_answer/"

    data = {"query": query, "documents_selected": documents_selected}
    headers = {"accept": "application/json"}

    response = requests.get(url=LLM_API_URL, params=data, headers=headers)

    if response.status_code == 200:
        return response.json()["index"]
    return None
