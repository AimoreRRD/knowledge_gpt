import json
import logging
from typing import List

from fastapi import FastAPI, File, UploadFile
from langchain.embeddings import HuggingFaceInstructEmbeddings

# from langchain.vectorstores import VectorStore
from langchain.vectorstores.faiss import FAISS
from pydantic import BaseModel

from document_store.parsers import parse_file
from document_store.texts_to_sub_documents import texts_to_sub_documents


class GenerateAnswerDataModel(BaseModel):
    query: str
    documents_selected: list
    k: int


app = FastAPI()
indexes = dict()

embedder = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post(("/load_embedder/"))
def load_embedder(model_name: str):
    global embedder
    if not embedder:
        logging.warning(f"Loading embedder: {model_name}")
        if model_name == "OpenAI":
            embedder = None
        else:
            embedder = HuggingFaceInstructEmbeddings(
                model_name=model_name,
                embed_instruction="Represent the question or text for retrieval:",
                query_instruction="Represent the context for retrieving supporting documents for questions:",
            )
    else:
        logging.warning(f"Embedder already loaded: {model_name}")


@app.post(("/doc_to_store/"))
async def doc_to_store(files: List[UploadFile] = File(...)):
    # TODO: Save the file locally
    document = files[0].file
    document_name = files[0].filename
    logging.warning(f"Adding document ({document_name}) to store.")

    # ? Parse
    logging.warning("Parsing.")
    text = parse_file(document, document_name)

    # ? Chunk + SubDocument
    logging.warning("Chunking and subdocumenting.")
    sub_documents, total_pages, total_chunks = texts_to_sub_documents(text, document_name)
    logging.warning(f"{len(sub_documents)=}")

    # ? Embed + Store
    logging.warning("Embedding all subdocuments and storing.")
    index = FAISS.from_documents(sub_documents, embedder)
    global indexes
    indexes[document_name] = index
    logging.warning(f"{indexes.keys()=}")

    document_metadata = dict(total_pages=total_pages, total_chunks=total_chunks)
    logging.warning(f"{document_metadata=}")
    return json.dumps(document_metadata)


@app.post("/get_selected_sources_with_scores/")
def get_selected_sources_with_scores(data: GenerateAnswerDataModel):
    data = data.dict()
    query = data["query"]
    documents_selected = data["documents_selected"]
    k = data["k"]

    logging.warning(
        f"Get {k} sources (subdocuments) for the selected documents: {documents_selected} based on the query: {query}"
    )

    sources_scores_list = []
    for documnet_name in documents_selected:
        index = indexes.get(documnet_name, dict())
        sources_scores = index.similarity_search_with_score(query, k=k)
        sources_scores = [(sources_score[0], 1 - sources_score[1]) for sources_score in sources_scores]
        sources_scores_list.extend(sources_scores)

    sources_scores_sorted = sorted(sources_scores_list, key=lambda x: x[1], reverse=True)
    from fastapi.encoders import jsonable_encoder

    return [(jsonable_encoder(x[0]), x[1]) for x in sources_scores_sorted]
