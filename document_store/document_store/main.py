
import json
from fastapi import FastAPI
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.vectorstores import VectorStore

from parses import parse_file
from texts_to_sub_documents import texts_to_sub_documents
from typing import List
from langchain.docstore.document import Document
from io import BytesIO

app = FastAPI()
indexes = dict()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/get_selected_sources_with_scores/")
async def get_selected_sources_with_scores(query:str, documents_selected:List[str]=[], k: int = 1) -> List[Document]:
    sources_scores_list = []
    for documnet_name in documents_selected:
        index = indexes.get(documnet_name, dict())
        sources_scores = index.similarity_search_with_score(query, k=k)
        sources_scores = [(sources_score[0], 1 - sources_score[1]) for sources_score in sources_scores]
        sources_scores_list.extend(sources_scores)

    sources_scores_sorted = sorted(sources_scores_list, key=lambda x: x[1], reverse=True)

    return sources_scores_sorted

@app.post(("/load_model/"))
def load_model(model_name: str="hkunlp/instructor-base"):
    global embedder
    embedder = HuggingFaceInstructEmbeddings(
        model_name=model_name,
        embed_instruction="Represent the question or text for retrieval:",
        query_instruction="Represent the context for retrieving supporting documents for questions:",
    )

@app.post(("/doc_to_store/"))
def doc_to_store(document: BytesIO):
    # ? Parse
    text = parse_file(document)

    document_name = document.str
    # ? Chunk + SubDocument
    sub_documents = texts_to_sub_documents(text, document_name)

    # ? Embed + Store
    index = FAISS.from_documents(sub_documents, embedder)

    indexes[document_name] = index
    