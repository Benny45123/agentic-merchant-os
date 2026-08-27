# AGENT_11_UAP_MACHINE_GATEWAY

## Objective

Build the Universal Agent Protocol (UAP) / Agent Commerce Protocol (ACP / AP2 / x402) Machine Discovery and Headless Agent-to-Agent (A2A) Purchase Gateway. Makes the merchant transactable by external AI buyers (ChatGPT, Claude, LangChain agents, AutoGPT) end-to-end without requiring a human UI.

## Scope

- `app/api/uap_gateway.py`: Router for public machine discovery and headless agent purchase
- `app/catalog/agent_manifest.py`: Dynamic generator for `/.well-known/agent.json` and Model Context Protocol (MCP) tool descriptors
- `app/guardian/machine_intent.py`: Headless transaction intent evaluator translating external A2A payloads to internal `TransactionIntentRequest`
- Test suite in `tests/test_uap_machine_gateway.py`

## Files/Directories Owned

`backend/app/api/uap_gateway.py`
`backend/app/catalog/agent_manifest.py`
`backend/tests/test_uap_machine_gateway.py`

## Dependencies

`app/catalog` (AGENT_02), `app/guardian` (AGENT_04), `app/mandate` (AGENT_04), `app/razorpay_adapter` (AGENT_05), `app/receipts` (AGENT_06).

## API Endpoints

### 1. `GET /.well-known/agent.json`
Public machine-readable manifest declaring:
- Protocol standard: `UAP-1.0`, `ACP-Draft`, `MCP-2024-11-05`
- Merchant ID and store capabilities
- Tool definitions (`search_catalog`, `get_authoritative_price`, `submit_signed_intent`)
- Payment rails supported (`razorpay_test_v1`)

### 2. `POST /agent/v1/machine-purchase`
Headless A2A purchase endpoint accepting:
```json
{
  "buyer_agent_id": "agent_gpt4_procure_007",
  "buyer_mandate": {
    "buyer_id": "b_001",
    "max_amount": 1000000,
    "max_quantity_per_item": 5,
    "currency": "INR",
    "signature": "sig_ed25519_buyer_mandate_attestation"
  },
  "purchase_items": [
    {
      "sku": "HP-001",
      "qty": 1,
      "observed_price": 449900,
      "catalog_version": 17
    }
  ],
  "agent_callback_url": "https://buyer-agent.internal/webhook/payment-ready"
}
```

Returns:
```json
{
  "status": "APPROVED",
  "guardian_decision": "APPROVE",
  "receipt_id": "rcpt_uuid_string",
  "final_verified_total": 449900,
  "razorpay_order_id": "order_test_xxxx",
  "payment_link": "https://api.razorpay.com/v1/checkout/hosted?order_id=order_test_xxxx",
  "replay_hash": "sha256_hash_of_decision_receipt"
}
```

## Implementation Requirements

1. Zero human UI interaction required: External AI agent can discover catalog, prepare purchase, pass mandate, receive Guardian validation, and execute payment via Razorpay test mode.
2. Every machine purchase must execute the full 22-case Guardian evaluation pipeline.
3. Every machine purchase must persist an immutable Decision Receipt tagged with `source: "uap_machine_agent"`.
4. Enforces strict cryptographic mandate signature validation or token authentication.

## Acceptance Criteria

- [ ] `GET /.well-known/agent.json` returns valid JSON with MCP tool schemas and store catalog version.
- [ ] `POST /agent/v1/machine-purchase` succeeds end-to-end for valid AI buyer intents.
- [ ] Headless purchase fails gracefully (`BLOCK`) if the AI buyer requests quantity > mandate limit or price < authoritative price.
- [ ] Pytest test cases pass with 100% code coverage in `tests/test_uap_machine_gateway.py`.
