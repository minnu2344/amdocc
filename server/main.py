from fastapi import FastAPI, Request
from server.models.generation import generate_explanation

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI!"}

@app.post("/api/v1/classify-text")
async def classifyText(request: Request):
    data = await request.json()
    text = data.get("text", "")
    original_statements, truth_values, explanations, sources_list = generate_explanation(text)
    return {"original_statements": original_statements, "truth_values": truth_values, "explanations": explanations, "sources_list": sources_list}