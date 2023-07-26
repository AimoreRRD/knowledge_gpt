from hashlib import md5
from typing import Any, Dict, List
from langchain.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

import streamlit as st
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import VectorStore
from langchain.vectorstores.faiss import FAISS
from openai.error import AuthenticationError
from langchain.embeddings import HuggingFaceInstructEmbeddings
from knowledge_gpt.prompts import STUFF_PROMPT


def hash_func(doc: Document) -> str:
    """Hash function for caching Documents"""
    return md5(doc.page_content.encode("utf-8")).hexdigest()


@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
    model = AutoModelForCausalLM.from_pretrained("distilgpt2", use_safetensors=False)
    pipe = pipeline(
        "text-generation", model=model, tokenizer=tokenizer, max_new_tokens=40, device=0
    )
    hf = HuggingFacePipeline(pipeline=pipe)

    # hf = HuggingFacePipeline.from_model_id(
    #             # model_id="gpt2",
    #             model_id="distilgpt2",
    #             task="text-generation",
    #             pipeline_kwargs={"max_new_tokens": 20},
    #             device=0
    #         )

    return hf

@st.cache_resource
def load_embeddings(model_name="hkunlp/instructor-base"):
    embeddings = HuggingFaceInstructEmbeddings(
            # model_name="hkunlp/instructor-large",
            # model_name="intfloat/e5-large-v2",
            model_name=model_name,
            embed_instruction="Represent the text for retrieval:",
            query_instruction="Represent the context for retrieving supporting documents:",
        )
    return embeddings

@st.cache_data(show_spinner="Indexing document... This may take a while⏳", hash_funcs={Document: hash_func})
def embed_docs(docs: List[Document], _embeddings=None) -> VectorStore:
    """Embeds a list of Documents and returns a FAISS index"""

    # if not st.session_state.get("OPENAI_API_KEY"):
        # raise AuthenticationError(
        #     "Enter your OpenAI API key in the sidebar. You can get a key at"
        #     " https://platform.openai.com/account/api-keys."
        # )
    # else:
    #? Embed the chunks
    # embeddings = OpenAIEmbeddings(
    #     openai_api_key=st.session_state.get("OPENAI_API_KEY"),
    # )  # type: ignore
    # else:
        

    index = FAISS.from_documents(docs, _embeddings)

    return index

# @st.cache_data(show_spinner=False, hash_funcs={Document: hash_func})
def get_answer(docs: List[Document], query: str, _model=None) -> Dict[str, Any]:
    """Gets an answer to a question from a list of Documents."""
    # if api_key:
    #     model = ChatOpenAI(temperature=0, openai_api_key=st.session_state.get("OPENAI_API_KEY")),  # type: ignore
    # Get the answer
    chain = load_qa_with_sources_chain(
        _model,
        chain_type="stuff",
        prompt=STUFF_PROMPT,
    )
    answer = chain({"input_documents": docs, "question": query}, return_only_outputs=True)
    return answer