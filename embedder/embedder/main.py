
import json
from fastapi import FastAPI
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores.faiss import FAISS

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/embed/")
async def embed_document(docs):
    print(f"docs:{docs}")
    print(type(json.loads(docs)))
    
    index = FAISS.from_documents(json.loads(docs), embedder)
    return index

@app.post(("/load_model/"))
def load_model(model_name: str):
    global embedder
    embedder = HuggingFaceInstructEmbeddings(
        model_name="hkunlp/instructor-base",
        embed_instruction="Represent the question or text for retrieval:",
        query_instruction="Represent the context for retrieving supporting documents for questions:",
    )
