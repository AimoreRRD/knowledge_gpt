import json

import requests
from streamlit.runtime.uploaded_file_manager import UploadedFile


def load_embedder(model_name: str):
    EMBEDDING_API_URL = "http://0.0.0.0:8532/load_embedder/"
    params = {"model_name": model_name}
    requests.post(url=EMBEDDING_API_URL, params=params)

    # if response.status_code == 200:
    #     return str(response.json())
    # return None


# def hash_func(doc: Document) -> str:
#     """Hash function for caching Documents"""
#     return md5(doc.page_content.encode("utf-8")).hexdigest()


# @st.cache_data(show_spinner="Indexing document... This may take a while⏳", hash_funcs={Document: hash_func})
def doc_to_store(uploaded_file: UploadedFile):
    DOC_STORE_API_URL = "http://0.0.0.0:8532/doc_to_store/"
    files = {"files": (uploaded_file.name, uploaded_file.read(), "application/pdf")}
    headers = {"accept": "application/json"}
    response = requests.post(url=DOC_STORE_API_URL, files=files, headers=headers)

    if response.status_code == 200:
        document_metadata = json.loads(response.json())
        print(f"{document_metadata=}")
        return document_metadata
    return None
