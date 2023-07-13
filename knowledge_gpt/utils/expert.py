from typing import Any, Dict, List

import streamlit as st
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.docstore.document import Document
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import VectorStore
from langchain.vectorstores.faiss import FAISS
from openai.error import AuthenticationError

from langchain.embeddings import OpenAIEmbeddings
from knowledge_gpt.prompts import STUFF_PROMPT

from hashlib import md5


def hash_func(doc: Document) -> str:
    """Hash function for caching Documents"""
    return md5(doc.page_content.encode("utf-8")).hexdigest()

@st.cache_data(show_spinner=False, hash_funcs={Document: hash_func})
def embed_docs(docs: List[Document]) -> VectorStore:
    """Embeds a list of Documents and returns a FAISS index"""

    if not st.session_state.get("OPENAI_API_KEY"):
        raise AuthenticationError(
            "Enter your OpenAI API key in the sidebar. You can get a key at"
            " https://platform.openai.com/account/api-keys."
        )
    else:
        # Embed the chunks
        embeddings = OpenAIEmbeddings(
            openai_api_key=st.session_state.get("OPENAI_API_KEY"),
        )  # type: ignore

        index = FAISS.from_documents(docs, embeddings)

        return index


@st.cache_data(show_spinner=False, hash_funcs={Document: hash_func})
def get_answer(docs: List[Document], query: str) -> Dict[str, Any]:
    """Gets an answer to a question from a list of Documents."""

    # Get the answer
    chain = load_qa_with_sources_chain(
        ChatOpenAI(
            temperature=0, openai_api_key=st.session_state.get("OPENAI_API_KEY")
        ),  # type: ignore
        chain_type="stuff",
        prompt=STUFF_PROMPT,
    )

    answer = chain(
        {"input_documents": docs, "question": query}, return_only_outputs=True
    )
    return answer


@st.cache_data(show_spinner=False, hash_funcs={Document: hash_func})
def get_sources(answer: Dict[str, Any], docs: List[Document]) -> List[Document]:
    """Gets the source documents for an answer."""

    # Get sources for the answer
    source_keys = [s for s in answer["output_text"].split("SOURCES: ")[-1].split(", ")]

    source_docs = []
    for doc in docs:
        if doc.metadata["source"] in source_keys:
            source_docs.append(doc)

    return source_docs
