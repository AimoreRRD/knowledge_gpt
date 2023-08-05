from fastapi import FastAPI

app = FastAPI()

@app.post("/test/")
async def generate_answer(question: str):
    # Your answering logic here
    # e.g., use chat-GPT or any other question-answering model
    return {"answer": "This is a placeholder answer."}  # Placeholder answer

@app.post("/generate/")
async def generate_answer_2(question: str):
    # Your answering logic here
    # e.g., use chat-GPT or any other question-answering model
    return {"answer": "This is a placeholder answer."}  # Placeholder answer
