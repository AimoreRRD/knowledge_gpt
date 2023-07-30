from typing import List

import streamlit as st
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceInstructEmbeddings, OpenAIEmbeddings
from langchain.vectorstores import VectorStore
from langchain.vectorstores.faiss import FAISS
from openai.error import AuthenticationError

from hashlib import md5



@st.cache_resource
def load_embedder(model_name):
    if model_name == "OpenAI":
        if not st.session_state.get("OPENAI_API_KEY"):
            raise AuthenticationError(
                "Enter your OpenAI API key in the sidebar. You can get a key at"
                " https://platform.openai.com/account/api-keys."
            )
        else:
            embedder = OpenAIEmbeddings(
                    openai_api_key=st.session_state.get("OPENAI_API_KEY"),
            )
    else:
        embedder = HuggingFaceInstructEmbeddings(
            # model_name="hkunlp/instructor-large",
            # model_name="intfloat/e5-large-v2",
            model_name=model_name,
            embed_instruction="Represent the question or text for retrieval:",
            query_instruction="Represent the context for retrieving supporting documents for questions:",
        )

    return embedder


def hash_func(doc: Document) -> str:
    """Hash function for caching Documents"""
    return md5(doc.page_content.encode("utf-8")).hexdigest()

@st.cache_data(show_spinner="Indexing document... This may take a while⏳", hash_funcs={Document: hash_func})
def embed_docs(docs: List[Document], _embedder=None) -> VectorStore:
    """Embeds a list of Documents and returns a FAISS index"""
    index = FAISS.from_documents(docs, _embedder)
    return index

