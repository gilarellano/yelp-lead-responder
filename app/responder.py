import logging
import anthropic

from app.config import ANTHROPIC_API_KEY
from app.models import YelpLead
from app.templates import SYSTEM_PROMPT, build_user_prompt, build_fallback_response

logger = logging.getLogger(__name__)


def generate_response(lead: YelpLead) -> str:
    if not ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not set — using fallback template")
        return build_fallback_response(lead)

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": build_user_prompt(lead)},
            ],
        )
        return message.content[0].text
    except Exception as e:
        logger.error("AI generation failed: %s — using fallback template", e)
        return build_fallback_response(lead)
