
# 19 — Environment Setup

## 1. Prerequisites

- Python 3.11+
- Node.js 20+ (for Next.js frontend)
- `git` with `git worktree` support (standard in modern git)
- A Razorpay account with **test-mode** API keys ([VERIFY current signup/keys flow at https://razorpay.com/docs/])
- An LLM provider API key (Gemini API key by default; Groq/OpenRouter optional — see `app/ai_provider`)
- (Optional, only if Razorpay webhook local delivery requires it — **[VERIFY]**) a tunneling tool such as `ngrok` for exposing `localhost` to Razorpay's webhook sender during test-mode development

## 2. Repository Layout Recap

```
/frontend
/backend
/docs
/AGENT_TASKS
```

## 3. Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt --break-system-packages   # or omit flag inside a venv
cp .env.example .env      # fill in secrets, see §5
alembic upgrade head       # or the chosen migration tool per AGENT_01
python -m app.seed         # loads default policy + demo catalog + demo buyer/mandate
uvicorn app.main:app --reload --port 8000
```

## 4. Frontend Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev   # http://localhost:3000
```

## 5. Required Environment Variables (`.env` — backend)

| Variable                    | Purpose                                            |
| --------------------------- | -------------------------------------------------- |
| `DATABASE_URL`            | e.g.`sqlite+aiosqlite:///./amos.db`              |
| `RAZORPAY_KEY_ID`         | test-mode key,`rzp_test_...`                     |
| `RAZORPAY_KEY_SECRET`     | test-mode secret — never commit, never log        |
| `RAZORPAY_WEBHOOK_SECRET` | for webhook signature verification                 |
| `LLM_PROVIDER`            | `gemini` (default) \| `groq` \| `openrouter` |
| `GEMINI_API_KEY`          | required if`LLM_PROVIDER=gemini`                 |
| `JWT_SIGNING_KEY`         | random secret for session tokens                   |
| `ENV`                     | `local` (only supported value for MVP)           |

## 6. Required Environment Variables (`.env.local` — frontend)

| Variable                        | Purpose                                                          |
| ------------------------------- | ---------------------------------------------------------------- |
| `NEXT_PUBLIC_API_BASE_URL`    | `http://localhost:8000`                                        |
| `NEXT_PUBLIC_RAZORPAY_KEY_ID` | same test-mode public key as backend, safe to expose client-side |

## 7. Seed Data Contents (`python -m app.seed`)

- 1 `Merchant` row
- 8-12 `Product` rows spanning 2-3 categories, including the headphones/warranty/case bundle trio and one product with an intentionally injected malicious `description` fixture (used by `13_THREAT_MODEL.md` item 1 test and `15_DEMO_SCENARIOS.md` Beat 5)
- 1 default `MerchantPolicy` (values in `08_MANDATE_AND_POLICY_SPEC.md` §7)
- 1 default `CampaignPolicy`
- 1 demo `Buyer` with an active `Mandate`

## 8. Running Tests

```bash
cd backend
pytest                              # all unit + integration tests
python scripts/check_import_graph.py   # architecture boundary lint
python scripts/run_scenarios.py     # end-to-end demo scenario scripts
```

## 9. Razorpay Test Mode Notes

- **[VERIFY against current docs]** exact test card numbers, test UPI VPA, and any test-mode-specific quirks before demo rehearsal — these are documented by Razorpay and can change.
- **[VERIFY]** whether webhook delivery to `localhost` requires a tunnel in the current Razorpay dashboard configuration, or whether a manual "resend webhook" / test-mode simulate button suffices for local development.

## 10. Common Setup Issues

| Symptom                                  | Likely Cause                                                                                                                                |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `alembic upgrade head` fails           | Wrong`DATABASE_URL` scheme (needs async driver, e.g. `aiosqlite`)                                                                       |
| Razorpay Checkout widget doesn't open    | `NEXT_PUBLIC_RAZORPAY_KEY_ID` missing or mismatched with backend's `RAZORPAY_KEY_ID`                                                    |
| Webhook never received locally           | No public tunnel configured — see §9                                                                                                      |
| Import-graph lint fails on a clean clone | A dependency was added in the wrong package — check`03_COMPONENT_ARCHITECTURE.md` ownership before adding cross-package imports          |
| LLM calls fail silently                  | Missing/invalid`GEMINI_API_KEY` — check `app/ai_provider` logs, never swallow this error into a default APPROVE anywhere near Guardian |
