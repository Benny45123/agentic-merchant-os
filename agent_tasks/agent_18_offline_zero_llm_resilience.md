# AGENT_18: 100% Offline Zero-LLM Fallback & Quota Resilience

## Objective
Harden the conversational commerce pipeline in `backend/app/commerce_agent/` and `backend/app/ai_provider/` so that if the Gemini / OpenAI API key is missing, network is offline, or rate limits (HTTP 429) occur, the system degrades seamlessly to a deterministic, category-grounded fallback with zero user-facing errors.

## Deliverables
1. `backend/app/ai_provider/gemini_provider.py`:
   - Catch quota / network / missing key exceptions cleanly without raising 500 errors.
   - Return structured deterministic fallback completions grounded in SQLite product catalog.
2. `backend/app/commerce_agent/graph.py` & `service.py`:
   - Guarantee that all conversational actions (`add`, `view details`, `recommend upsell`, `checkout`, `undo`) succeed 100% reliably in offline mode.
   - Maintain the deterministic Commerce Guardian gatekeeper on all transactions.

## Acceptance Criteria
- Running with an empty `GEMINI_API_KEY=""` or no internet connection still allows full end-to-end chat, cart addition, upsell recommendation, and checkout.
