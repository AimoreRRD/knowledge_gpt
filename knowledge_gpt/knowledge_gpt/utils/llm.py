from typing import Any, Dict, List

import streamlit as st
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.llms import HuggingFacePipeline
from prompts import STUFF_PROMPT
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline


@st.cache_resource
def load_llm(model_name):
    if model_name == "OpenAI":
        llm = ChatOpenAI(temperature=0, openai_api_key=st.session_state.get("OPENAI_API_KEY"))  # type: ignore
    else:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name, use_safetensors=False)
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=50, device=0)
        llm = HuggingFacePipeline(pipeline=pipe)

        # pipeline = HuggingFacePipeline.from_model_id(
        #             # model_id="gpt2",
        #             model_id="distilgpt2",
        #             task="text-generation",
        #             pipeline_kwargs={"max_new_tokens": 20},
        #             device=0
        #         )

    return llm


# @st.cache_data(show_spinner=False, hash_funcs={Document: hash_func})
def get_answer(docs: List[Document], query: str, _llm) -> Dict[str, Any]:
    """Gets an answer to a question from a list of Documents."""
    chain = load_qa_with_sources_chain(
        _llm,
        chain_type="stuff",
        prompt=STUFF_PROMPT,
    )
    answer = chain({"input_documents": docs, "question": query}, return_only_outputs=False)
    return answer
