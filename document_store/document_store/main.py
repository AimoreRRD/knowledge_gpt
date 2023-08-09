import logging
from typing import List

from fastapi import FastAPI, File, UploadFile
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceInstructEmbeddings

# from langchain.vectorstores import VectorStore
from langchain.vectorstores.faiss import FAISS

from document_store.parsers import parse_file
from document_store.texts_to_sub_documents import texts_to_sub_documents

app = FastAPI()
indexes = dict()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/get_selected_sources_with_scores/")
async def get_selected_sources_with_scores(
    query: str, documents_selected: List[str] = [], k: int = 1
) -> List[Document]:
    print("get_selected_sources_with_scores...")
    sources_scores_list = []
    for documnet_name in documents_selected:
        index = indexes.get(documnet_name, dict())
        sources_scores = index.similarity_search_with_score(query, k=k)
        sources_scores = [(sources_score[0], 1 - sources_score[1]) for sources_score in sources_scores]
        sources_scores_list.extend(sources_scores)

    sources_scores_sorted = sorted(sources_scores_list, key=lambda x: x[1], reverse=True)

    return {"sources_scores_sorted": sources_scores_sorted}


@app.post(("/load_model/"))
def load_model(model_name: str):
    print(f"{model_name=}", flush=True)
    global embedder
    if model_name == "OpenAI":
        embedder = None
    else:
        embedder = HuggingFaceInstructEmbeddings(
            model_name=model_name,
            embed_instruction="Represent the question or text for retrieval:",
            query_instruction="Represent the context for retrieving supporting documents for questions:",
        )


@app.post(("/doc_to_store/"))
async def doc_to_store(files: List[UploadFile] = File(...)):
    # TODO: Save the file locally
    document = files[0].file
    document_name = files[0].filename
    logging.warning(f"\ndocument_name: {document_name}")
    logging.warning(f"\ndocument: {type(document)}")

    # ? Parse
    text = parse_file(document, document_name)

    # ? Chunk + SubDocument
    sub_documents = texts_to_sub_documents(text, document_name)
    print(f"{len(sub_documents)=}", flush=True)

    # ? Embed + Store
    index = FAISS.from_documents(sub_documents, embedder)

    indexes[document_name] = index
