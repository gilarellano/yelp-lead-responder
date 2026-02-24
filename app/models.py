from pydantic import BaseModel
from typing import Optional

class YelpLead(BaseModel):
  customer_name: str
  job_type: Optional[str] = None
  zip_code: Optional[str] = None
  message: Optional[str] = None
  survey_answers: Optional[str] = None
  image_urls: Optional[str] = None
  lead_created_at: Optional[str] = None