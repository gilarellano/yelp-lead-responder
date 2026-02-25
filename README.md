# Yelp Lead Responder

Automated lead response system that receives Yelp leads via Zapier webhooks and generates personalized AI-powered responses using Claude.

## How It Works

1. A new lead comes in on Yelp
2. Zapier sends the lead data to this webhook
3. The lead is parsed, validated, and stored
4. An AI-generated personalized response is created using Claude
5. The response is returned and stored for tracking

## Setup

1. Copy the example environment file and configure it:
   ```bash
   cp app/.env.example .env
   ```

2. Fill in your environment variables in `.env`:
   - `API_KEY` - Secret key for authenticating Zapier webhook requests
   - `ANTHROPIC_API_KEY` - Your Anthropic API key for Claude
   - `BUSINESS_NAME` - Your business name (used in responses)
   - `BUSINESS_PHONE` - Your business phone number
   - `BUSINESS_EMAIL` - Your business contact email

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## Docker

```bash
docker compose -f app/docker-compose.yml up --build
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| POST | `/` | Receive webhook from Zapier |
| GET | `/leads` | List all leads with responses |
| GET | `/leads/{lead_id}` | Get a specific lead and its response |

## Zapier Configuration

Set up a Zapier Zap with:
- **Trigger**: Yelp - New Lead
- **Action**: Webhooks by Zapier - POST
- **URL**: Your ngrok/server URL
- **Headers**: `x-api-key: <your API_KEY>`
- **Body**: Map Yelp lead fields to the webhook payload
