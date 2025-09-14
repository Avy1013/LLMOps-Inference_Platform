from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

# Load model once at startup
classifier = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    device=-1  # CPU
)

class Request(BaseModel):
    text: str

class Response(BaseModel):
    label: str
    score: float

@app.post("/predict", response_model=Response)
def predict(req: Request):
    out = classifier(req.text)[0]
    return Response(label=out["label"], score=out["score"])