from fastapi import FastAPI
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores.faiss import FAISS

app = FastAPI()


@app.post("/embed/")
async def embed_document(docs):
    index = FAISS.from_documents(docs, embedder)
    return index

@app.post(("/load_model/{model_name}"))
async def load_model(model_name: str):
    global embedder
    embedder = HuggingFaceInstructEmbeddings(
        model_name=model_name,
        embed_instruction="Represent the question or text for retrieval:",
        query_instruction="Represent the context for retrieving supporting documents for questions:",
    )
    

@app.post("/embed/")
async def embed_document_2(text: str):
    # Your embedding logic here
    # e.g., use chat-GPT or any other embedding model
    return {"embedding": [0.1, 0.2, 0.3]}  # Placeholder embedding result
