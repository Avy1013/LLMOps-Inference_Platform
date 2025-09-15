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

@app.post("/generate", response_model=Response, dependencies=[Depends(verify_credits)])
def generate(req: Request):
    out = generator(
        req.prompt,
        max_new_tokens=64,
        do_sample=False,
        temperature=0.2,
        top_p=0.9,
        repetition_penalty=1.2,
        return_full_text=False,
        num_return_sequences=1,
    )[0]
    return Response(generated_text=out["generated_text"])

