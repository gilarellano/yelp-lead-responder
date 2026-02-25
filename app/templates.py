from app.models import YelpLead
from app.config import BUSINESS_NAME, BUSINESS_PHONE, BUSINESS_EMAIL

SYSTEM_PROMPT = f"""You are a friendly, professional customer service representative for {BUSINESS_NAME}.
Your job is to write a warm, personalized first response to a new customer lead from Yelp.

Guidelines:
- Address the customer by their first name
- Acknowledge their specific needs based on the job type and message
- Be warm and professional but not overly formal
- Keep the response concise (3-5 sentences)
- If they described their problem, show you understood it
- Express enthusiasm about helping them
- End with a clear next step (scheduling a call, free estimate, etc.)
- Include contact info: phone {BUSINESS_PHONE}, email {BUSINESS_EMAIL}
- Do NOT use markdown formatting — write plain text suitable for a Yelp message"""


def build_user_prompt(lead: YelpLead) -> str:
    parts = [f"Customer name: {lead.customer_name}"]

    if lead.job_type:
        parts.append(f"Job type: {lead.job_type}")
    if lead.zip_code:
        parts.append(f"Zip code: {lead.zip_code}")
    if lead.message:
        parts.append(f"Customer message: {lead.message}")
    if lead.survey_answers:
        parts.append(f"Survey answers: {lead.survey_answers}")
    if lead.image_urls:
        parts.append("The customer attached photos of the job.")

    return (
        "Write a personalized response to this new Yelp lead:\n\n"
        + "\n".join(parts)
    )


FALLBACK_TEMPLATE = """Hi {first_name},

Thank you for reaching out to {business_name} through Yelp! We received your inquiry{job_mention} and would love to help.

We'd like to learn more about your needs so we can provide the best service possible. Feel free to give us a call at {phone} or reply to this message, and we'll get back to you right away.

Looking forward to working with you!

Best regards,
{business_name}"""


def build_fallback_response(lead: YelpLead) -> str:
    first_name = lead.customer_name.split()[0] if lead.customer_name else "there"
    job_mention = f" about {lead.job_type}" if lead.job_type else ""

    return FALLBACK_TEMPLATE.format(
        first_name=first_name,
        business_name=BUSINESS_NAME,
        job_mention=job_mention,
        phone=BUSINESS_PHONE,
    )
