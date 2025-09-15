from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from transformers import pipeline
import httpx
import os

# --- Credit Service Dependency ---
CREDIT_SERVICE_URL = os.getenv("CREDIT_SERVICE_URL", "http://credit-service/check")

async def verify_credits(x_consumer_username: str = Header(...)):
    """
    This is a FastAPI Dependency. It runs before the main endpoint logic.
    It calls the credit service to verify and deduct credits.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Forward the username header to the credit service
            headers = {'X-Consumer-Username': x_consumer_username}
            response = await client.post(CREDIT_SERVICE_URL, headers=headers)

            # If the credit service returns an error, raise it immediately
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        # Pass the error from the credit service back to the end-user
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json().get("detail"))
    except Exception:
        # Handle cases where the credit service might be down
        raise HTTPException(status_code=503, detail="Credit service is currently unavailable.")

# --- Application ---
app = FastAPI()

# Load model once at startup
classifier = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    device=-1  # CPU
)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/readyz")
def readyz():
    if classifier is None:
        raise HTTPException(status_code=503, detail="model not loaded")
    return {"status": "ready"}

class Request(BaseModel):
    text: str

class Response(BaseModel):
    label: str
    score: float

@app.post("/predict", response_model=Response, dependencies=[Depends(verify_credits)])
def predict(req: Request):
    out = classifier(req.text)[0]
    return Response(label=out["label"], score=out["score"])