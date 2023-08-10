from typing import Any, Dict

import requests
import streamlit as st


@st.cache_data
def load_llm(model_name, openai_api_key):
    LLM_API_URL = "http://0.0.0.0:8533/load_model/"

    data = {"model_name": model_name, "openai_api_key": openai_api_key}
    headers = {"accept": "application/json"}

    response = requests.post(url=LLM_API_URL, params=data, headers=headers)

    if response.status_code == 200:
        return response.json()
    return None


# @st.cache_data(show_spinner=False, hash_funcs={Document: hash_func})
def get_answer(query: str, documents_selected: list) -> Dict[str, Any]:
    LLM_API_URL = "http://0.0.0.0:8533/generate/"

    params = {"query": query}
    data = {"documents_selected": documents_selected}

    headers = {"accept": "application/json"}
    print(f"{data=}")
    response = requests.post(url=LLM_API_URL, params=params, data=data, headers=headers)
    # answer = response.json()["answer"]["output_text"]
    
    answer = response.json()["answer"]
    docs_resources = response.json()["docs_resources"]
    if response.status_code == 200:
        return answer, docs_resources
    return None
