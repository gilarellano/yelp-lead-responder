from fastapi import FastAPI, Request, HTTPException
from pydantic import ValidationError
from dotenv import load_dotenv
from app.models import YelpLead
import os
import json

load_dotenv()

app = FastAPI()

API_KEY = os.getenv("API_KEY")

@app.get("/")
async def webhook_check():
  return {"status": "ok"}

@app.post("/")
async def webhook(request: Request):
  api_key = request.headers.get("x-api-key")
  if api_key != API_KEY:
    raise HTTPException(status_code=401, detail="Unauthorized")

  try:
    raw = await request.json()
  except Exception:
    body = await request.body()
    print(f"[DEBUG] Could not parse request as JSON. Raw body: {body}")
    return {"status": "received"}

  try:
    lead = YelpLead(**raw)
    print(f"[YelpLead] {lead}")
  except (ValidationError, TypeError):
    print(f"[DEBUG] Payload did not match YelpLead schema. Raw payload:\n{json.dumps(raw, indent=2)}")

  return {"status": "received"}