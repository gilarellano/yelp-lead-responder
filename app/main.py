import logging
from fastapi import FastAPI, Request, HTTPException
from pydantic import ValidationError

from app.config import API_KEY
from app.models import YelpLead
from app.store import init_db, save_lead, get_lead, get_all_leads, update_lead_response
from app.responder import generate_response

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Yelp Lead Responder")


@app.on_event("startup")
async def startup():
    init_db()
    logger.info("Database initialized")


@app.get("/")
async def health_check():
    return {"status": "ok"}


@app.post("/")
async def webhook(request: Request):
    api_key = request.headers.get("x-api-key")
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    body = await request.json()
    logger.info("Received webhook payload for: %s", body.get("customer_name", "unknown"))

    try:
        lead = YelpLead(**body)
    except ValidationError as e:
        logger.error("Validation error: %s", e)
        raise HTTPException(status_code=422, detail=str(e))

    lead_id = save_lead(lead)
    logger.info("Saved lead #%d: %s", lead_id, lead.customer_name)

    response_text = generate_response(lead)
    update_lead_response(lead_id, response_text)
    logger.info("Generated response for lead #%d", lead_id)

    return {
        "status": "responded",
        "lead_id": lead_id,
        "customer_name": lead.customer_name,
        "response": response_text,
    }


@app.get("/leads")
async def list_leads():
    leads = get_all_leads()
    return {"leads": leads, "count": len(leads)}


@app.get("/leads/{lead_id}")
async def get_lead_detail(lead_id: int):
    lead = get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
