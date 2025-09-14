from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

# Load text-generation model
generator = pipeline(
    "text-generation",
    model="distilgpt2",
    device=-1  # CPU
)

class Request(BaseModel):
    prompt: str

class Response(BaseModel):
    generated_text: str

@app.post("/generate", response_model=Response)
def generate(req: Request):
    out = generator(req.prompt, max_length=30, num_return_sequences=1)[0]
    return Response(generated_text=out["generated_text"])

