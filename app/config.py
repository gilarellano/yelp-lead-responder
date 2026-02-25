import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "Our Business")
BUSINESS_PHONE = os.getenv("BUSINESS_PHONE", "")
BUSINESS_EMAIL = os.getenv("BUSINESS_EMAIL", "")
DATABASE_PATH = os.getenv("DATABASE_PATH", "leads.db")
