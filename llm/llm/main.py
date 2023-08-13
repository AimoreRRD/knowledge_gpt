import json
import logging

import requests
from fastapi import FastAPI
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.llms import HuggingFacePipeline
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline


class GenerateAnswerDataModel(BaseModel):
    query: str
    documents_selected: list
    k: int


app = FastAPI()

chain = None
current_model_name = None


@app.post(("/load_llm/"))
async def load_llm(model_name, openai_api_key, device):
    global current_model_name

    if model_name != current_model_name:
        logging.warning(f"Loading LLM: {model_name}")
        global chain
        current_model_name = model_name
        if model_name == "OpenAI":
            llm = ChatOpenAI(temperature=0, openai_api_key=openai_api_key)
        else:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name, use_safetensors=False)
            pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=50, device=device)
            llm = HuggingFacePipeline(pipeline=pipe)

        chain = load_qa_with_sources_chain(
            llm,
            chain_type="stuff",
            prompt=STUFF_PROMPT,
        )
        logging.warning(f"chain {chain=} ")
        logging.warning(f"llm: {llm=}")


@app.post("/generate/")
def generate_answer(data: GenerateAnswerDataModel):
    query = data.dict()["query"]
    documents_selected = data.dict()["documents_selected"]
    logging.warning(f"Generating answer for query: {query} based on documents_selected: {documents_selected}")

    DOC_STORE_API_URL = "http://0.0.0.0:8532/get_selected_sources_with_scores/"

    response = requests.post(url=DOC_STORE_API_URL, data=json.dumps(data.dict()))

    if response.status_code == 200:
        sources_scores_sorted = response.json()
        docs_resources = [
            Document(page_content=x[0]["page_content"], metadata=x[0]["metadata"]) for x in sources_scores_sorted
        ]

        # response = [[{'page_content': "Sir Isaac Newton FRS Portrait of Newton at 46 by Godfrey Kneller, 1689 Born 4 January 1643 [O.S. 25 December 1642][a] Woolsthorpe-by-Colsterworth, Lincolnshire, England Died 31 March 1727 (aged 84) [O.S. 20 March 1726][a] Kensington, Middlesex, Great Britain Resting placeWestminster Abbey Education Trinity College, Cambridge (M.A., 1668)[15] Known for List Newtonian mechanics universal gravitation calculus Newton's laws of motion optics binomial series PrincipiaIsaac Newton Sir Isaac Newton FRS", 'metadata': {'document_name': 'Isaac_Newton.pdf', 'page': 1, 'chunk': 0, 'total_pages': 35, 'total_chunks': 6, 'source': 'Isaac_Newton.pdf-1-0'}}, 0.769099622964859],]

        # TODO: Cap the lenght of the docs resources + Context Stuff to the maximum capacity of the model

        answer = chain({"input_documents": docs_resources, "question": query}, return_only_outputs=True)
        logging.warning(f"answer: {answer}")

        return {"answer": answer["output_text"], "sources_scores_sorted": sources_scores_sorted}
    else:
        logging.warning(f"\n{response.status_code=}")
        logging.warning(f"\n{response.content=}")


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

template = """
You are an AI that helps me to answer questions.
Answer the QUESTION based on your knowledge and use the CONTEXT as a reference of extra knowledge:\n
CONTEXT:\n
{summaries}
\n
QUESTION:\n
{question}
"""
logging.warning(f"template: {len(template)}")
STUFF_PROMPT = PromptTemplate(template=template, input_variables=["summaries", "question"])
