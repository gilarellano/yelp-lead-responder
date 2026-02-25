from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class YelpLead(BaseModel):
    customer_name: str
    job_type: Optional[str] = None
    zip_code: Optional[str] = None
    message: Optional[str] = None
    survey_answers: Optional[str] = None
    image_urls: Optional[str] = None
    lead_created_at: Optional[str] = None


class LeadRecord(BaseModel):
    id: int
    customer_name: str
    job_type: Optional[str] = None
    zip_code: Optional[str] = None
    message: Optional[str] = None
    survey_answers: Optional[str] = None
    image_urls: Optional[str] = None
    lead_created_at: Optional[str] = None
    response_text: Optional[str] = None
    status: str = "new"
    created_at: str = ""
    responded_at: Optional[str] = None
