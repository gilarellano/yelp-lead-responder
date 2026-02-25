# Yelp Lead Responder — MVP Build Plan

## Overview

When a new Yelp lead comes in, the system:
1. Parses the lead (customer message + images)
2. Runs image(s) through a vision model → produces structured **image tags**
3. Runs the message through a text model → produces structured **message tags**
4. A router uses both tag sets to select the best **response template**
5. Sends you an **email/SMS** with the lead summary + AI-suggested response
6. You **approve or edit** and send — that action triggers Zapier → Yelp messaging
7. Every interaction is **stored** (lead + AI suggestion + your final response) for future fine-tuning

---

## Current State

| File | Status | Notes |
|---|---|---|
| `app/main.py` | ✅ Done | Webhook receives lead, parses JSON, validates into `YelpLead` |
| `app/models.py` | ✅ Done | `YelpLead` pydantic model |
| `app/templates.py` | 🔲 Empty | Placeholder only |
| `requirements.txt` | ⚠️ Partial | Missing AI SDKs, test libs, notifier libs |
| `Dockerfile` / `docker-compose.yml` | ✅ Exists | Already set up for deployment |

---

## Final Directory Structure

```
yelp-lead-responder/
├── app/
│   ├── main.py                   # FastAPI app — webhook entry point (done)
│   ├── models.py                 # YelpLead pydantic model (done)
│   ├── tags.py                   # Tag vocabulary — enums/constants for all valid tags
│   ├── templates.py              # Template definitions — conditions + response text
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── image_analyzer.py     # Calls vision model, returns image tags
│   │   └── message_classifier.py # Calls text model, returns message tags
│   ├── router.py                 # Matches tag combinations to a template
│   ├── notifier.py               # Formats and sends email/SMS to you
│   ├── approver.py               # Approval endpoint — receives your action, triggers Zapier
│   └── storage.py                # Saves lead + AI suggestion + final response to disk/DB
│
├── data/
│   └── leads/                    # Stored lead history (JSONL, one record per lead)
│
├── evals/
│   ├── sample_leads.json         # 20–30 hand-picked real leads with expected outputs
│   ├── run_classifier_eval.py    # Runs message classifier against sample set, prints accuracy
│   └── run_image_eval.py         # Runs image analyzer against sample images, prints accuracy
│
├── tests/
│   ├── test_models.py            # Unit: YelpLead parsing edge cases
│   ├── test_router.py            # Unit: given tag sets, does router return correct template?
│   ├── test_notifier.py          # Unit: does notifier format the message correctly?
│   ├── test_approver.py          # Unit: does approval endpoint store + trigger correctly?
│   └── test_storage.py           # Unit: read/write lead records correctly
│
├── .env                          # Secrets (never commit)
├── .env.example                  # Template for required env vars
├── requirements.txt
├── ngrok.yml
├── Dockerfile
├── docker-compose.yml
└── PLAN.md                       # This file
```

---

## Tag Vocabulary (Design Before Everything Else)

Tags are the contract between the analysis layer and the template layer.
**These must be finalized before building analyzers or templates.**

### Image Tags
| Tag | Meaning |
|---|---|
| `broken_glass` | Cracked or shattered glass pane |
| `wood_rot` | Visible wood rot or decay on frame |
| `failed_seal` | Fogged/condensation between panes |
| `existing_frame` | Photo of current installed window frame |
| `exterior_shot` | Full exterior of home or building |
| `interior_shot` | View from inside looking at window |
| `measurement` | Tape measure, ruler, or written dimensions visible |
| `drawing_sketch` | Hand-drawn or printed diagram |
| `no_image` | Lead came with no images |
| `unclear` | Image too blurry or unrelated to windows |

### Message Tags
| Tag | Meaning |
|---|---|
| `repair` | Customer needs a fix, not a full replacement |
| `replacement` | Existing window needs to be swapped out |
| `new_install` | New construction or addition |
| `quote_request` | Asking for a price estimate |
| `urgent` | Language suggests time pressure ("ASAP", "emergency", etc.) |
| `general_inquiry` | Vague or exploratory — not a specific job yet |
| `measurement_needed` | They don't have dimensions yet |
| `measurement_provided` | Dimensions included in message or survey answers |
| `multi_window` | Job involves more than one window |
| `single_window` | Job involves one window |
| `historic_building` | SF historic property context mentioned |

> **Note:** Both lists can grow as you encounter real leads. Design templates
> to handle combinations of 2–3 tags rather than requiring an exact full match.

---

## Template Design (Informed by Tags)

Each template has:
- A **name** (human-readable)
- A **trigger condition** (which tag combinations activate it)
- A **priority** (when multiple templates match, highest priority wins)
- A **response body** (the actual message, with optional fill-in placeholders)

### Example Template Routing Logic

```
IF broken_glass OR wood_rot OR failed_seal → "repair" family
  + urgent → Template: Emergency Repair Response
  + no urgent → Template: Standard Repair Inquiry Response

IF replacement OR new_install → "install" family
  + measurement_provided → Template: Quote Ready Response
  + measurement_needed → Template: Measurement Request Response
  + multi_window → Template: Multi-Window Project Response

IF general_inquiry AND no specific job tags → Template: General Greeting Response
```

> Define at least **6–8 templates** to start. They can be plain text with
> `{customer_name}` and `{job_type}` placeholders for personalization.

---

## Build Order (Phase by Phase)

Each phase follows the TDD cycle:
**write test → write code → green → move on**

---

### Phase 0 — Tag Vocabulary & Templates *(No code — design only)*
> Do this before writing a single line of new code.

- [ ] Finalize the image tag list (review your real leads, what do you actually see?)
- [ ] Finalize the message tag list (review your 1.4k message history for patterns)
- [ ] Write out 6–8 template responses in plain text
- [ ] Map each template to its tag trigger conditions
- [ ] Document all of the above in `app/tags.py` (as constants) and `app/templates.py`

---

### Phase 1 — Template Router *(Pure logic, no AI — easiest to TDD)*
> Build the matching engine before building the things that feed it.
> This is 100% deterministic — perfect for TDD.

- [ ] `app/tags.py` — define tag enums/constants
- [ ] `app/templates.py` — define templates with trigger conditions
- [ ] `app/router.py` — given a set of image tags + message tags, return best template
- [ ] `tests/test_router.py` — unit test every template trigger condition
  - Test: `broken_glass + urgent` → returns Emergency Repair template
  - Test: `replacement + measurement_provided` → returns Quote Ready template
  - Test: no matching tags → returns General Greeting (fallback)

---

### Phase 2 — Message Classifier *(First AI component)*
> Start with text before images — easier to debug, cheaper to iterate.

- [ ] `app/analyzers/message_classifier.py`
  - Accepts: `message: str`, `survey_answers: Optional[str]`
  - Returns: list of message tags from the vocabulary
  - Prompt strategy: few-shot (pick 5–10 examples from your 1.4k history per tag)
- [ ] `evals/sample_leads.json` — build a set of 20–30 known leads with expected tag outputs
- [ ] `evals/run_classifier_eval.py` — run classifier against sample set, print accuracy
- [ ] Tune the prompt until eval accuracy is acceptable (aim for ~85%+ before moving on)

---

### Phase 3 — Image Analyzer *(Second AI component)*
> Same structure as Phase 2, but using the vision model.

- [ ] `app/analyzers/image_analyzer.py`
  - Accepts: `image_urls: Optional[str]` (comma-separated or list)
  - Returns: list of image tags from the vocabulary
  - Handles `no_image` case cleanly (don't call the model if no URLs)
- [ ] Add image test cases to `evals/sample_leads.json`
- [ ] `evals/run_image_eval.py` — run against sample images, print accuracy
- [ ] Tune the prompt until accuracy is acceptable

---

### Phase 4 — Wire Analyzers into Webhook *(Integration)*
> Connect the pieces: lead → analyze → route → log result.
> No notification yet — just confirm the full pipeline runs end-to-end.

- [ ] Update `app/main.py` to call both analyzers and the router after parsing `YelpLead`
- [ ] Print the full result to console (tags + selected template name) for now
- [ ] Test manually with ngrok + Zapier using a real or simulated Yelp lead
- [ ] Confirm correct template is selected for 3–5 different lead types

---

### Phase 5 — Notifier *(Email/SMS to you)*
> You should now receive a formatted message with the lead + AI suggestion.

- [ ] `app/notifier.py`
  - Formats: customer name, job type, message, image tags, message tags, suggested template text
  - Includes: Approve link, Edit link (both pointing to your approval endpoint)
  - Sends via: email (Resend or SendGrid) — SMS optional for MVP
- [ ] `tests/test_notifier.py` — unit test formatting logic (not the actual send)
- [ ] Test manually: trigger a lead, receive the email, confirm it looks right

---

### Phase 6 — Approver & Storage *(Close the loop)*
> The last mile: your approval triggers the response, and everything is saved.

- [ ] `app/approver.py`
  - New endpoint: `POST /approve`
  - Accepts: `lead_id`, `final_response` (approved or edited text)
  - Triggers Zapier webhook → Zapier sends response to Yelp messaging
- [ ] `app/storage.py`
  - Saves to `data/leads/` as JSONL
  - Record schema: `lead`, `image_tags`, `message_tags`, `template_used`, `ai_suggestion`, `final_response`, `was_edited`, `timestamp`
- [ ] `tests/test_approver.py` — unit test the endpoint logic
- [ ] `tests/test_storage.py` — unit test read/write
- [ ] End-to-end test: real lead → notification received → approve → check Yelp for the reply

---

### Phase 7 — Hardening *(Before using in production)*
> Make it reliable enough to trust with real customers.

- [ ] Add error handling: what if the vision model fails? what if Zapier is down?
- [ ] Add logging (structured, not just `print`) — consider `loguru`
- [ ] Add a timeout on AI calls so the webhook doesn't hang
- [ ] Rate limiting on the webhook endpoint
- [ ] Add `.env.example` with all required keys documented
- [ ] Smoke test the full flow 3 times with real leads before going live

---

## Tools & Services Needed

### Python Packages to Add to `requirements.txt`
| Package | Purpose |
|---|---|
| `openai` | GPT-4o vision + text API |
| `anthropic` | Claude API (text classification) |
| `httpx` | Async HTTP calls (Zapier webhook trigger) |
| `pytest` | Unit testing |
| `pytest-asyncio` | Async test support for FastAPI |
| `resend` or `sendgrid` | Email notification to you |
| `loguru` | Structured logging (replaces `print`) |

### External Services
| Service | Purpose | Notes |
|---|---|---|
| **OpenAI API** | GPT-4o for vision (image analyzer) | `platform.openai.com` |
| **Anthropic API** | Claude for message classification | `console.anthropic.com` |
| **Resend** | Email notifications to you | `resend.com` — generous free tier, simple API |
| **Zapier** | Already in use — add outbound webhook step for sending Yelp replies | No changes to existing setup, just add a new Zap step |
| **ngrok** | Already in use — expose local server for testing | Keep using as-is |

### Dev Tools
| Tool | Purpose | Where |
|---|---|---|
| `promptfoo` | LLM eval framework — run your sample leads against prompts | `promptfoo.dev` |
| `pytest` | Standard TDD test runner | `pytest.org` |
| Postman or `httpie` | Manually fire test webhooks | `postman.com` or `httpie.io` |

---

## Testing Strategy Summary

| Layer | Tool | What gets tested |
|---|---|---|
| Models & parsing | `pytest` | `YelpLead` edge cases, missing fields, bad input |
| Router | `pytest` | Every tag combination → correct template |
| Notifier | `pytest` | Message formatting, placeholder substitution |
| Approver & Storage | `pytest` | Endpoint logic, file I/O correctness |
| Message classifier | `promptfoo` / eval script | Prompt accuracy against 20–30 real leads |
| Image analyzer | `promptfoo` / eval script | Vision model accuracy against sample images |
| Full pipeline | Manual (ngrok + Zapier) | End-to-end smoke test with a real Yelp lead |

---

## Feedback Loop / Future Fine-Tuning

Every lead stored in `data/leads/` is a future training record.

Once you have ~100+ records where `was_edited = true`:
1. Extract pairs: `(customer_message, ai_suggestion)` vs `(customer_message, final_response)`
2. Format as OpenAI JSONL fine-tuning file
3. Run fine-tuning job on `gpt-4o-mini` via OpenAI API
4. Swap the base model in `message_classifier.py` for your fine-tuned model ID
5. Re-run evals to confirm improvement

> **Search:** `"OpenAI fine-tuning guide JSONL format"` when ready for this step.

---

## Key Env Variables Needed (`.env`)

```
API_KEY=             # Your webhook auth key (already set)
OPENAI_API_KEY=      # For GPT-4o vision
ANTHROPIC_API_KEY=   # For Claude text classification
RESEND_API_KEY=      # For email notifications
NOTIFY_EMAIL=        # Your email address for approvals
ZAPIER_WEBHOOK_URL=  # Outbound Zapier hook to send Yelp reply
```