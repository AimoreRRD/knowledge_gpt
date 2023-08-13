import json
import logging

import requests


def load_llm(model_name, openai_api_key, device):
    LLM_API_URL = "http://0.0.0.0:8533/load_llm/"

    data = {"model_name": model_name, "openai_api_key": openai_api_key, "device": device}
    headers = {"accept": "application/json"}

    response = requests.post(url=LLM_API_URL, params=data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        logging.warning(response.status_code)
        logging.warning(response.content)


# @st.cache_data(show_spinner=False, hash_funcs={Document: hash_func})
def get_answer(query: str, documents_selected: list, k: int):
    print("get_answer...")
    LLM_API_URL = "http://0.0.0.0:8533/generate/"

    data = {"query": query, "documents_selected": documents_selected, "k": k}
    response = requests.post(url=LLM_API_URL, data=json.dumps(data))

    if response.status_code == 200:
        full_answer = response.json()
        answer = full_answer["answer"]
        sources_scores_sorted = full_answer["sources_scores_sorted"]
        return answer, sources_scores_sorted
    else:
        logging.warning(response.status_code)
        logging.warning(response.content)
        return None, None
