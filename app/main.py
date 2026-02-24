from fastapi import FastAPI, Request
import json

app = FastAPI()

@app.get("/")
async def webhook_check():
    return {"status": "ok"}

@app.post("/")
async def webhook(request: Request):
    raw = await request.json()
    print(json.dumps(raw, indent=2))
    return {"status": "received"}