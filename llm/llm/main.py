from typing import List

import requests
from fastapi import FastAPI
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

app = FastAPI()


@app.post(("/load_model/{model_name}"))
async def load_model(model_name: str):
    global llm

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, use_safetensors=False)
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=50, device=0)
    llm = HuggingFacePipeline(pipeline=pipe)


@app.get("/generate/")
async def generate_answer(question: str, documents_selected: List[str]):
    chain = load_qa_with_sources_chain(
        llm,
        chain_type="stuff",
        prompt=STUFF_PROMPT,
    )

    DOC_STORE_API_URL = "http://0.0.0.0:8532/get_selected_sources_with_scores/"
    data = {"query": question, "documents_selected": documents_selected, "k": 1}

    response = requests.get(url=DOC_STORE_API_URL, params=data)
    print(f"response:{response}")
    print(response)
    docs_resources = response

    answer = chain({"input_documents": docs_resources, "question": question}, return_only_outputs=False)

    return {"answer": answer}


# flake8: noqa
from langchain.prompts import PromptTemplate

## Use a shorter template to reduce the number of tokens in the prompt
template = """Create a final answer to the given questions using the provided document excerpts(in no particular order) as references.
ALWAYS include a "SOURCES" section in your answer including only the minimal set of sources needed to answer the question.
If you are unable to answer the question, simply state that you do not know. Do not attempt to fabricate an answer and leave the SOURCES section empty.

---------

QUESTION: What  is the purpose of ARPA-H?
=========
Content: More support for patients and families. \n\nTo get there, I call on Congress to fund ARPA-H, the Advanced Research Projects Agency for Health. \n\nIt’s based on DARPA—the Defense Department project that led to the Internet, GPS, and so much more.  \n\nARPA-H will have a singular purpose—to drive breakthroughs in cancer, Alzheimer’s, diabetes, and more.
Source: 1-32
Content: While we’re at it, let’s make sure every American can get the health care they need. \n\nWe’ve already made historic investments in health care. \n\nWe’ve made it easier for Americans to get the care they need, when they need it. \n\nWe’ve made it easier for Americans to get the treatments they need, when they need them. \n\nWe’ve made it easier for Americans to get the medications they need, when they need them.
Source: 1-33
Content: The V.A. is pioneering new ways of linking toxic exposures to disease, already helping  veterans get the care they deserve. \n\nWe need to extend that same care to all Americans. \n\nThat’s why I’m calling on Congress to pass legislation that would establish a national registry of toxic exposures, and provide health care and financial assistance to those affected.
Source: 1-30
=========
FINAL ANSWER: The purpose of ARPA-H is to drive breakthroughs in cancer, Alzheimer’s, diabetes, and more.
SOURCES: 1-32

---------

QUESTION: {question}
=========
{summaries}
=========
FINAL ANSWER:"""

STUFF_PROMPT = PromptTemplate(template=template, input_variables=["summaries", "question"])
