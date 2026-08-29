# AGENT_16: Headless AI Buyer CLI Simulator

## Objective
Build a standalone, headless CLI simulator (`scripts/simulate_ai_buyer.py` and `bin/simulate_ai_buyer.sh`) that autonomously interacts with the Agentic Merchant OS via the Universal Agent Protocol (UAP) without needing a web browser.

## Deliverables
1. `scripts/simulate_ai_buyer.py`:
   - Queries `GET /api/uap/catalog` for available products and snapshot IDs.
   - Formulates volume procurement RFQ for smartphones or laptops.
   - Posts `POST /api/uap/quote` to negotiate dynamic B2B pricing.
   - Evaluates multi-option counter-offers (Price discount vs Bundle sweetener).
   - Settles transaction via `POST /api/uap/settle`.
   - Logs full thought trace with ANSI colors.
2. `bin/simulate_ai_buyer.sh`:
   - Executable wrapper script ensuring backend is healthy and executing the simulation with 1 click.

## Acceptance Criteria
- Running `./bin/simulate_ai_buyer.sh` executes the full negotiation flow in < 2 seconds.
- Results appear in the merchant `/dashboard` live telemetry feed and `/receipts` explorer.
