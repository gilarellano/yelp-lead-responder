from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
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
    print(json.dumps(raw, indent=2))
  except Exception:
    raw = await request.body()
    print(f"Raw body: {raw}")
  
  return {"status": "received"}