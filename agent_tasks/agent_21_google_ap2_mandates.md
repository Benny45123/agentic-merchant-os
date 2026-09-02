# Agent Task: Agent 21 — Google AP2 Open vs. Closed Mandate Chains (ES256)

## Context & Purpose
Implement the official **Google Agent Payments Protocol (AP2)** specification within Agentic Merchant OS. Establish an asymmetric ECDSA (ES256) cryptographic delegation chain:
1. The human shopper signs an **Open Mandate JWT** delegating an aggregate spending ceiling.
2. The purchasing agent signs a transaction-specific **Closed Mandate JWT** binding the canonical cart digest (`SHA-256`).
3. The **Commerce Guardian** deterministically verifies both ES256 signatures, checks parent-child linkage, verifies the cart digest against authoritative catalog data, and commits the AP2 leaf to the Decision Receipt and Merkle Tree before Razorpay recurring settlement.

---

## Deliverables

### 1. Cryptographic Mandate Service (`backend/app/mandate/ap2_service.py`)
- Implement key generation and storage for ECDSA P-256 keypairs (`generate_es256_keypair()`).
- Implement `mint_open_mandate(buyer_id, agent_id, max_amount_paise, autopay_token, private_key)` returning signed ES256 JWT.
- Implement `mint_closed_mandate(open_mandate_jwt, intent_items, amount_paise, agent_private_key)` computing canonical cart digest and returning signed ES256 JWT.
- Implement `verify_ap2_mandate_chain(open_jwt, closed_jwt, expected_items, user_public_key, agent_public_key)` returning verification verdict and error code.

### 2. Database Models & Schema Extensions (`backend/app/models/mandate.py`)
- Extend `BuyerMandate` model with:
  - `open_mandate_jwt: Optional[str]`
  - `user_public_key_pem: Optional[str]`
  - `agent_public_key_pem: Optional[str]`
- Update `MandateResponse` in `backend/app/mandate/schemas.py` to expose AP2 verification status and public keys.

### 3. Commerce Guardian Dual-Chain Verification Gate (`backend/app/guardian/pipeline.py`)
- Integrate AP2 validation into `evaluate_transaction_intent`:
  - Verify Open Mandate signature against stored `user_public_key`.
  - Verify Closed Mandate signature against stored `agent_public_key`.
  - Confirm `closed_mandate.parent_mandate_id == open_mandate.jti`.
  - Recompute cart digest from authoritative catalog prices:
    $$\text{digest} = \text{SHA256}(\text{canonical\_json}(\text{items}))$$
  - Ensure `digest == closed_mandate.cart_digest`.
  - Record deterministic invariant checks in the signed Decision Receipt:
    - `ap2.open_mandate_verified: PASSED`
    - `ap2.closed_mandate_verified: PASSED`
    - `ap2.cart_digest_verified: PASSED`
    - `ap2.chain_linkage_verified: PASSED`
  - Deterministically block with `REJECTED_AP2_INTEGRITY_FAIL` if any signature or digest check fails.

### 4. Decision Receipts & Merkle Tree Visualizer (`backend/app/receipts/` & Frontend)
- In `app/receipts/service.py`:
  - Embed `open_mandate_jti`, `closed_mandate_jti`, and `cart_digest` into Decision Receipt metadata.
  - Add 4th leaf ($L_4 = H_{\text{AP2}}$) to the receipt Merkle tree:
    $$H_{\text{AP2}} = \text{SHA256}(\text{open\_jti} \parallel \text{closed\_jti} \parallel \text{cart\_digest})$$
- In `frontend/src/components/MerkleTreeVisualizer.tsx`:
  - Render the balanced 4-leaf Merkle Tree:
    $$(H_{\text{cart}} \parallel H_{\text{policy}}) \parallel (H_{\text{sig}} \parallel H_{\text{AP2}}) \rightarrow H_{\text{root}}$$

### 5. Client & Agent Tool Integration
- In `backend/app/api/mcp_server.py`:
  - Expose `get_ap2_mandate_chain(buyer_id)` MCP tool returning active Open Mandate and cryptographic details.
- In `backend/app/telegram/handlers.py`:
  - Attach AP2 Closed Mandate generation to Telegram 1-click purchases.

### 6. Automated Pytest Test Suite
- Create `backend/tests/test_google_ap2_mandates.md`:
  - Test valid ES256 Open-to-Closed chain verification.
  - Test tampering detection: cart item SKU manipulation, quantity tampering, price inflation.
  - Test expired Closed Mandate rejection.
  - Test invalid parent mandate reference rejection.

---

## Acceptance Criteria
- [ ] Open Mandate JWT signed with ES256 and verified using NIST P-256 public key.
- [ ] Closed Mandate JWT binds canonical cart digest `SHA-256` for line-item non-repudiation.
- [ ] Guardian executes 4-point AP2 verification gate in under 10ms.
- [ ] Any item price or SKU tampering causes instant `AP2_CART_DIGEST_MISMATCH` rejection.
- [ ] Decision Receipts and Merkle Tree Visualizer include the $H_{\text{AP2}}$ leaf.
- [ ] 100% backward compatible with existing Razorpay UPI AutoPay token flow.
