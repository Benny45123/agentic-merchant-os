# Document 24: Google AP2 Open vs. Closed Mandate Specification (ES256)

## 1. Executive Summary

The **Agent Payments Protocol (AP2)** standardizes cryptographic delegation for autonomous artificial intelligence transactions. In high-trust agentic commerce, an autonomous agent must possess verifiably bounded purchasing power without ever having unilateral or unconstrained access to a merchant's payment rails.

Agentic Merchant OS implements the **Google AP2 Dual-Chain Mandate Specification**:
1. **Open Mandate (Human Delegator $\rightarrow$ Agent)**: An **ES256-signed JWT** created when the user establishes a spending budget (e.g., ₹1,00,000 via Headless Razorpay UPI AutoPay). It encodes aggregate financial bounds, permitted channels, expiration, and the user's public key.
2. **Closed Mandate (Agent $\rightarrow$ Commerce Guardian)**: An **ES256-signed JWT** minted dynamically by the purchasing AI agent for a single specific transaction. It cryptographically chains to the parent Open Mandate and binds the authoritative SHA-256 cart digest.
3. **Commerce Guardian Verification Kernel**: The Zero-LLM Commerce Guardian mathematically verifies both ECDSA signatures, validates the cart digest against authoritative catalog pricing, confirms spend headroom, and records the AP2 audit chain in the Decision Receipt and Merkle Tree prior to calling Razorpay.

---

## 2. Cryptographic Delegation Hierarchy

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                           HUMAN USER (b_001)                            │
│           Possesses Private Key (K_user_priv, ES256 / P-256)            │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                 Signs Open Mandate  │ [Budget: ₹1,00,000, 90 Days]
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     GOOGLE AP2 OPEN MANDATE (JWT)                       │
│  • jti: mnd_open_8f29c41a0e9b                                           │
│  • sub: urn:agent:commerce_agent_01                                     │
│  • cap: max_total_paise: 10000000, max_per_charge: 5000000             │
│  • payment_rail: razorpay_upi_autopay (tok_rzp_autopay_...)             │
│  • sig: ES256(K_user_priv, Header + Claims)                            │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                      Chained at     │ Autonomous Purchase Intent:
                      Checkout Time  │ Buy HP-001 (Headphones) @ ₹4,499
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    GOOGLE AP2 CLOSED MANDATE (JWT)                      │
│  • jti: mnd_closed_4c3b2a1e0f8d                                         │
│  • parent_mandate_id: mnd_open_8f29c41a0e9b                             │
│  • cart_digest: SHA256(canonical_json([{"sku": "HP-001", ...}]))       │
│  • amount_paise: 449900                                                 │
│  • nonce: nonce_91a82f3b4c                                              │
│  • sig: ES256(K_agent_priv, Header + Claims)                           │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
           Both Tokens Submitted     │ Sub-50ms Deterministic Check
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    COMMERCE GUARDIAN DUAL-CHAIN GATE                    │
│  ✓ 1. Verify Open Mandate Signature (K_user_pub)                        │
│  ✓ 2. Verify Closed Mandate Signature (K_agent_pub)                     │
│  ✓ 3. Verify parent_mandate_id == Open Mandate jti                      │
│  ✓ 4. Compute Intent Cart Digest == Closed Mandate cart_digest          │
│  ✓ 5. Closed Mandate Amount (₹4,499) ≤ Open Mandate Headroom            │
│  ✓ 6. Rule 6 Gross Margin Floor ≥ 15%                                   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                 PASS (Deterministic)│ Zero OTP Debit (<400ms)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                RAZORPAY TEST API & DECISION RECEIPTS                    │
│  • Executes charge_autopay_token()                                      │
│  • Mints Decision Receipt embedding AP2 Open/Closed Mandate Hash        │
│  • Appends 4th Leaf to Cryptographic Merkle Tree Visualizer (H_AP2)     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Canonical Cart Digest Algorithm

To prevent man-in-the-middle manipulation, the Closed Mandate binds the exact cart contents via a canonical SHA-256 digest:

$$\text{cart\_digest} = \text{SHA-256}(\text{canonical\_json}(\text{items}))$$

### Canonical Representation Rules:
1. Items are sorted lexicographically by `sku` in ascending order.
2. Each item contains strictly `sku` (string), `quantity` (integer), and `price_paise` (integer).
3. No extraneous whitespace, keys sorted alphabetically, standard UTF-8 encoding.

### Example:
```json
[{"price_paise":449900,"quantity":1,"sku":"HP-001"}]
```
$$\text{cart\_digest} = \text{7a38b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3}$$

If an adversary attempts to modify the SKU to `AU-001` or alter the price, the digest verification fails instantly with `AP2_CART_DIGEST_MISMATCH`.

---

## 4. JWT Claim Specifications (ES256 / RFC 7515)

### 4.1 Open Mandate Payload
* `iss` (*string*): Issuer URI of the human shopper (e.g. `urn:buyer:b_001`).
* `sub` (*string*): Subject URI of the authorized agent (e.g. `urn:agent:commerce_agent_01`).
* `aud` (*string*): Target merchant identifier (`urn:merchant:agentic_merchant_os`).
* `jti` (*string*): Unique Mandate Identifier (e.g. `mnd_open_...`).
* `iat` (*integer*): Issued-at Unix epoch timestamp.
* `exp` (*integer*): Expiration Unix epoch timestamp.
* `nbf` (*integer*): Not-before Unix epoch timestamp.
* `mandate_type` (*string*): `"GOOGLE_AP2_OPEN_MANDATE"`.
* `cap` (*object*):
  * `max_total_paise` (*integer*): Maximum lifetime budget for this mandate cycle.
  * `max_per_charge_paise` (*integer*): Maximum allowable single-transaction debit.
  * `currency` (*string*): Currency identifier (`"INR"`).
* `payment_rail` (*object*):
  * `type` (*string*): `"razorpay_upi_autopay"`.
  * `token_id` (*string*): Linked Razorpay recurring token (`tok_rzp_autopay_...`).
  * `customer_id` (*string*): Razorpay customer ID.
* `user_public_key_jwk` (*object*): ECDSA P-256 public key of the human user in JWK format.

### 4.2 Closed Mandate Payload
* `iss` (*string*): Issuer URI of the purchasing agent (`urn:agent:commerce_agent_01`).
* `sub` (*string*): Subject URI of the transaction intent (`urn:intent:{tx_intent_id}`).
* `aud` (*string*): Verifier URI (`urn:guardian:commerce_guardian`).
* `jti` (*string*): Unique Closed Mandate Identifier (e.g. `mnd_closed_...`).
* `iat` (*integer*): Issued-at timestamp.
* `exp` (*integer*): Short-lived expiration (typically `iat + 60s`).
* `mandate_type` (*string*): `"GOOGLE_AP2_CLOSED_MANDATE"`.
* `parent_mandate_id` (*string*): References the Open Mandate `jti`.
* `cart_digest` (*string*): Canonical SHA-256 hash of the order line items.
* `amount_paise` (*integer*): Transaction charge amount in paise.
* `currency` (*string*): `"INR"`.
* `nonce` (*string*): Anti-replay cryptographic nonce.

---

## 5. Merkle Tree & Audit Trail Integration

In the existing Decision Receipts system (`/receipts/[id]`), the Merkle Tree contains 3 leaves:
* $L_1$: Cart Digest ($H_{\text{cart}}$)
* $L_2$: Policy Snapshot Digest ($H_{\text{policy}}$)
* $L_3$: Guardian Signature ($H_{\text{sig}}$)

Under Google AP2, a **4th cryptographic leaf** is integrated into the tree:
$$L_4 = H_{\text{AP2}} = \text{SHA-256}(\text{open\_jti} \parallel \text{closed\_jti} \parallel \text{cart\_digest})$$

The 4-leaf Merkle root becomes:
$$\text{Merkle Root} = \text{SHA-256}(\text{SHA-256}(L_1 \parallel L_2) \parallel \text{SHA-256}(L_3 \parallel L_4))$$

This provides undeniable cryptographic proof that every cent charged over Razorpay was explicitly authorized by a human-signed Open Mandate and bound to an agent-signed Closed Mandate.
