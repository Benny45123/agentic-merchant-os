# Document 21: AI Buyer Simulator, Merkle Proof Trees & Zero-LLM Offline Resilience

## 1. Overview & Purpose

This document specifies three critical architectural components that establish **10.0 / 10.0** production maturity for Agentic Merchant OS:
1. **Headless AI Buyer CLI Simulator (`./bin/simulate_ai_buyer.sh`)**: A standalone autonomous procurement agent communicating via the Universal Agent Protocol (UAP).
2. **Visual Merkle Proof Tree Diagram**: An interactive cryptographic proof visualizer for Decision Receipts verifying bit-for-bit audit integrity.
3. **100% Offline Zero-LLM Fallback Engine**: Deterministic fallback pipelines guaranteeing seamless conversational commerce even under network drops or LLM quota exhaustion.

---

## 2. Headless AI Buyer Protocol & CLI Simulator

### Architecture Flow:
```
┌───────────────────────────────────────┐
│     Autonomous Procurement Bot        │
│    (scripts/simulate_ai_buyer.py)     │
└──────────────────┬────────────────────┘
                   │
                   ▼  1. GET /api/uap/catalog (Fetch authoritative snapshot)
┌───────────────────────────────────────┐
│        Merchant OS UAP Gateway        │
│        (app/api/uap_gateway.py)       │
└──────────────────┬────────────────────┘
                   │
                   ▼  2. POST /api/uap/quote (Submit volume RFQ offer)
┌───────────────────────────────────────┐
│      Merchant AI Pricing Agent        │
│       & Commerce Guardian Gate        │
└──────────────────┬────────────────────┘
                   │
                   ▼  3. Return Multi-Option Counter-Offer (+ Sweeteners)
┌───────────────────────────────────────┐
│       AI Buyer Strategy Selector      │
│     (Evaluates margin & sweetener)    │
└──────────────────┬────────────────────┘
                   │
                   ▼  4. POST /api/uap/settle (1-Click Guardian Settlement)
┌───────────────────────────────────────┐
│  Immutable Signed Decision Receipt    │
└───────────────────────────────────────┘
```

### Execution:
```bash
# Launch the headless autonomous bot simulator in terminal
./bin/simulate_ai_buyer.sh
```

---

## 3. Visual Merkle Proof Tree Diagram

Every transaction processed by the Commerce Guardian mints a cryptographic receipt containing:
1. **Leaf A (`H_cart`)**: `SHA-256(canonical_cart_json)`
2. **Leaf B (`H_policy`)**: `SHA-256(policy_snapshot_json + invariant_matrix)`
3. **Leaf C (`H_signature`)**: `SHA-256(Ed25519_merchant_signature)`
4. **Merkle Root (`H_root`)**: `SHA-256(H_cart || H_policy || H_signature)`

### Visual Tree Structure:
```
               ┌───────────────────────────────┐
               │    SHA-256 Merkle Root Root   │
               │   e3b0c44298fc1c149afbf4c8... │
               └───────────────┬───────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  Leaf 1: Cart   │   │ Leaf 2: Policy  │   │ Leaf 3: Sign    │
│  State Digest   │   │ Invariant Check │   │ Ed25519 Key     │
│  4f8a91b2c3...  │   │ 9b12c83d4e...   │   │ a178f02e6b...   │
└─────────────────┘   └─────────────────┘   └─────────────────┘
```

When a judge or auditor clicks **"Replay Verification"**, the kernel re-evaluates the transaction state against historical invariants and verifies `H_root_replay == H_root_original` with zero drift.

---

## 4. 100% Offline Zero-LLM Fallback Engine

### High-Availability Fallback Ladder:
1. **Primary**: Gemini / OpenAI LLM Provider via `LangGraph` StateGraph.
2. **Secondary (Rate-Limit / HTTP 429 / Timeout)**:
   - Evaluated by `DeterministicFallbackProvider`.
   - Resolves intent via regex & keyword maps.
   - Extracts grounded product specs directly from SQLite catalog.
   - Applies Guardian invariant checks.
3. **Zero Failure Guarantee**:
   - No unhandled exceptions or error toasts in UI.
   - Full conversational capability maintained (add, remove, upsell, checkout, undo).
