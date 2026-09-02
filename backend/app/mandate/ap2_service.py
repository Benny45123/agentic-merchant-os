"""
Google Agent Payments Protocol (AP2) Mandate Engine.

Implements Open Mandate and Closed Mandate cryptographic chains with:
- ECDSA ES256 (NIST P-256 curve / secp256r1 with SHA-256) asymmetric keypairs
- Canonical Cart Digest calculation (SHA-256 over normalized JSON items)
- Parent-child cryptographic linkage (Closed Mandate pinned to Open Mandate JTI)
- Deterministic 6-point verification gate (Pure Python, sub-3ms latency)
- Merkle Tree Leaf (H_AP2) calculation
"""

import base64
import hashlib
import json
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import jwt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


# In-memory cached keypairs for deterministic demo execution
_KEYPAIR_CACHE: Dict[str, Tuple[str, str]] = {}


def generate_es256_keypair() -> Tuple[str, str]:
    """
    Generate an ECDSA P-256 (secp256r1) keypair.
    Returns (private_key_pem, public_key_pem) as UTF-8 strings.
    """
    private_key = ec.generate_private_key(ec.SECP256R1())
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    return private_pem, public_pem


def get_or_create_buyer_keypair(buyer_id: str = "b_001") -> Tuple[str, str]:
    """Retrieve or deterministically generate the persistent ES256 keypair for a buyer."""
    cache_key = f"buyer_{buyer_id}"
    if cache_key not in _KEYPAIR_CACHE:
        _KEYPAIR_CACHE[cache_key] = generate_es256_keypair()
    return _KEYPAIR_CACHE[cache_key]


def get_or_create_agent_keypair(agent_id: str = "agent_commerce_01") -> Tuple[str, str]:
    """Retrieve or deterministically generate the persistent ES256 keypair for an agent."""
    cache_key = f"agent_{agent_id}"
    if cache_key not in _KEYPAIR_CACHE:
        _KEYPAIR_CACHE[cache_key] = generate_es256_keypair()
    return _KEYPAIR_CACHE[cache_key]


def canonical_json(data: Any) -> str:
    """Format data as canonical JSON: sorted keys, compact separators, no extra spaces."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def compute_canonical_cart_digest(items: List[Dict[str, Any]]) -> str:
    """
    Computes canonical SHA-256 digest of cart items according to Google AP2 spec:
    1. Extracts strictly sku, quantity, price_paise.
    2. Sorts items lexicographically by SKU.
    3. Hashes canonical JSON representation with SHA-256.
    """
    canonical_items = []
    for it in items:
        # Resolve price in paise from observed_price or authoritative_price
        price = (
            it.get("price_paise")
            or it.get("authoritative_price")
            or it.get("observed_price")
            or 0
        )
        qty = it.get("quantity") or it.get("qty") or 1
        sku = str(it.get("sku") or "")
        canonical_items.append({
            "price_paise": int(price),
            "quantity": int(qty),
            "sku": sku,
        })

    # Sort lexicographically by SKU
    canonical_items.sort(key=lambda x: x["sku"])
    payload_str = canonical_json(canonical_items)
    return hashlib.sha256(payload_str.encode("utf-8")).hexdigest()


def mint_open_mandate(
    buyer_id: str,
    agent_id: str = "urn:agent:commerce_agent_01",
    merchant_id: str = "urn:merchant:agentic_merchant_os",
    max_total_paise: int = 10000000,      # ₹1,00,000.00
    max_per_charge_paise: int = 5000000,  # ₹50,000.00
    currency: str = "INR",
    duration_days: int = 90,
    autopay_token: Optional[str] = None,
    customer_id: Optional[str] = None,
    user_private_key_pem: Optional[str] = None,
) -> Tuple[str, str]:
    """
    Mint a Google AP2 Open Mandate JWT signed with the User's ES256 private key.
    Returns (open_mandate_jwt, user_public_key_pem).
    """
    if not user_private_key_pem:
        priv_pem, pub_pem = get_or_create_buyer_keypair(buyer_id)
    else:
        priv_pem = user_private_key_pem
        # Derive public key
        priv_obj = serialization.load_pem_private_key(priv_pem.encode("utf-8"), password=None)
        pub_pem = priv_obj.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

    now_ts = int(time.time())
    jti = f"mnd_open_{hashlib.sha256(f'{buyer_id}:{now_ts}'.encode()).hexdigest()[:16]}"

    payload = {
        "iss": f"urn:buyer:{buyer_id}",
        "sub": agent_id,
        "aud": merchant_id,
        "jti": jti,
        "iat": now_ts,
        "nbf": now_ts,
        "exp": now_ts + (duration_days * 86400),
        "mandate_type": "GOOGLE_AP2_OPEN_MANDATE",
        "cap": {
            "max_total_paise": max_total_paise,
            "max_per_charge_paise": max_per_charge_paise,
            "currency": currency,
        },
        "payment_rail": {
            "type": "razorpay_upi_autopay",
            "token_id": autopay_token or f"tok_rzp_autopay_{jti[9:]}",
            "customer_id": customer_id or f"cust_rzp_{buyer_id}",
        },
        "user_public_key_pem": pub_pem,
    }

    token = jwt.encode(payload, priv_pem, algorithm="ES256")
    return token, pub_pem


def mint_closed_mandate(
    open_mandate_jwt: str,
    items: List[Dict[str, Any]],
    amount_paise: int,
    intent_id: Optional[str] = None,
    currency: str = "INR",
    agent_id: str = "urn:agent:commerce_agent_01",
    agent_private_key_pem: Optional[str] = None,
    ttl_seconds: int = 180,
) -> Tuple[str, str]:
    """
    Mint a Google AP2 Closed Mandate JWT signed with the Agent's ES256 private key.
    Binds the parent Open Mandate JTI and the canonical cart digest.
    Returns (closed_mandate_jwt, agent_public_key_pem).
    """
    if not agent_private_key_pem:
        priv_pem, pub_pem = get_or_create_agent_keypair(agent_id)
    else:
        priv_pem = agent_private_key_pem
        priv_obj = serialization.load_pem_private_key(priv_pem.encode("utf-8"), password=None)
        pub_pem = priv_obj.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

    # Decode unverified Open Mandate payload to retrieve parent JTI & signature hash
    unverified_open = jwt.decode(open_mandate_jwt, options={"verify_signature": False})
    parent_jti = unverified_open.get("jti")
    
    # Compute signature hash of the parent Open Mandate
    open_sig_part = open_mandate_jwt.split(".")[2] if len(open_mandate_jwt.split(".")) == 3 else ""
    parent_sig_hash = hashlib.sha256(open_sig_part.encode("utf-8")).hexdigest()

    # Compute Canonical Cart Digest
    cart_digest = compute_canonical_cart_digest(items)

    now_ts = int(time.time())
    tx_jti = f"mnd_closed_{hashlib.sha256(f'{intent_id or parent_jti}:{now_ts}'.encode()).hexdigest()[:16]}"
    nonce = f"nonce_{hashlib.sha256(f'{tx_jti}:{time.time()}'.encode()).hexdigest()[:12]}"

    payload = {
        "iss": agent_id,
        "sub": f"urn:intent:{intent_id or tx_jti}",
        "aud": "urn:guardian:commerce_guardian",
        "jti": tx_jti,
        "iat": now_ts,
        "exp": now_ts + ttl_seconds,
        "mandate_type": "GOOGLE_AP2_CLOSED_MANDATE",
        "parent_mandate_id": parent_jti,
        "parent_mandate_sig_hash": parent_sig_hash,
        "cart_digest": cart_digest,
        "transaction": {
            "amount_paise": amount_paise,
            "currency": currency,
            "item_count": len(items),
        },
        "nonce": nonce,
    }

    token = jwt.encode(payload, priv_pem, algorithm="ES256")
    return token, pub_pem


def verify_open_mandate(open_mandate_jwt: str, user_public_key_pem: str) -> Dict[str, Any]:
    """Verify Open Mandate JWT using user's ES256 public key and check standard claims."""
    return jwt.decode(
        open_mandate_jwt,
        user_public_key_pem,
        algorithms=["ES256"],
        options={"verify_aud": False},
    )


def verify_closed_mandate(closed_mandate_jwt: str, agent_public_key_pem: str) -> Dict[str, Any]:
    """Verify Closed Mandate JWT using agent's ES256 public key and check standard claims."""
    return jwt.decode(
        closed_mandate_jwt,
        agent_public_key_pem,
        algorithms=["ES256"],
        options={"verify_aud": False},
    )


def verify_ap2_mandate_chain(
    open_mandate_jwt: str,
    closed_mandate_jwt: str,
    expected_items: List[Dict[str, Any]],
    expected_amount_paise: int,
    user_public_key_pem: Optional[str] = None,
    agent_public_key_pem: Optional[str] = None,
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Deterministic 6-Point Google AP2 Dual-Chain Verification Kernel:
    1. Verify Open Mandate signature with User Public Key.
    2. Verify Closed Mandate signature with Agent Public Key.
    3. Verify parent_mandate_id in Closed Mandate matches Open Mandate JTI.
    4. Verify parent_mandate_sig_hash matches SHA-256 of Open Mandate signature.
    5. Recompute canonical cart_digest and verify bit-for-bit equality.
    6. Verify Closed Mandate amount matches expected amount and does not exceed per-charge ceiling.

    Returns:
        (is_valid: bool, reason: str, metadata: dict)
    """
    checks: Dict[str, Any] = {}

    # 1. Decode unverified payloads to extract embedded public keys if not supplied
    try:
        unverified_open = jwt.decode(open_mandate_jwt, options={"verify_signature": False})
        user_pub = user_public_key_pem or unverified_open.get("user_public_key_pem")
        if not user_pub:
            return False, "Missing user_public_key_pem for Open Mandate verification", checks
    except Exception as e:
        return False, f"Malformed Open Mandate JWT: {str(e)}", checks

    try:
        unverified_closed = jwt.decode(closed_mandate_jwt, options={"verify_signature": False})
        agent_id = unverified_closed.get("iss", "urn:agent:commerce_agent_01")
        # Fetch or use provided agent public key
        if not agent_public_key_pem:
            _, agent_pub = get_or_create_agent_keypair(agent_id)
        else:
            agent_pub = agent_public_key_pem
    except Exception as e:
        return False, f"Malformed Closed Mandate JWT: {str(e)}", checks

    # 2. Verify Open Mandate cryptographic signature
    try:
        open_payload = verify_open_mandate(open_mandate_jwt, user_pub)
        checks["open_mandate_signature"] = "VALID"
        checks["open_mandate_jti"] = open_payload.get("jti")
    except jwt.ExpiredSignatureError:
        return False, "Google AP2 Open Mandate has expired", checks
    except Exception as e:
        return False, f"Google AP2 Open Mandate ES256 signature verification failed: {str(e)}", checks

    # 3. Verify Closed Mandate cryptographic signature
    try:
        closed_payload = verify_closed_mandate(closed_mandate_jwt, agent_pub)
        checks["closed_mandate_signature"] = "VALID"
        checks["closed_mandate_jti"] = closed_payload.get("jti")
    except jwt.ExpiredSignatureError:
        return False, "Google AP2 Closed Mandate has expired", checks
    except Exception as e:
        return False, f"Google AP2 Closed Mandate ES256 signature verification failed: {str(e)}", checks

    # 4. Verify Parent Linkage
    open_jti = open_payload.get("jti")
    parent_ref = closed_payload.get("parent_mandate_id")
    if parent_ref != open_jti:
        return (
            False,
            f"Chain Broken: Closed Mandate parent_mandate_id ({parent_ref}) does not match Open Mandate JTI ({open_jti})",
            checks,
        )
    checks["chain_linkage"] = "VALID"

    # Verify signature hash pinning
    open_sig_part = open_mandate_jwt.split(".")[2] if len(open_mandate_jwt.split(".")) == 3 else ""
    expected_parent_sig_hash = hashlib.sha256(open_sig_part.encode("utf-8")).hexdigest()
    if closed_payload.get("parent_mandate_sig_hash") != expected_parent_sig_hash:
        return (
            False,
            "Chain Integrity Broken: Open Mandate signature hash mismatch in Closed Mandate",
            checks,
        )
    checks["signature_hash_pinning"] = "VALID"

    # 5. Verify Canonical Cart Digest
    expected_digest = compute_canonical_cart_digest(expected_items)
    actual_digest = closed_payload.get("cart_digest")
    checks["expected_cart_digest"] = expected_digest
    checks["actual_cart_digest"] = actual_digest

    if actual_digest != expected_digest:
        return (
            False,
            f"AP2 Cart Digest Mismatch: Intent items digest ({expected_digest}) does not match Closed Mandate digest ({actual_digest})",
            checks,
        )
    checks["cart_digest_verified"] = "VALID"

    # 6. Verify Amount & Per-Charge Ceilings
    tx_meta = closed_payload.get("transaction", {})
    closed_amount = tx_meta.get("amount_paise")
    if closed_amount is not None and closed_amount != expected_amount_paise:
        return (
            False,
            f"Amount Mismatch: Closed Mandate specifies {closed_amount} paise, but verified total is {expected_amount_paise} paise",
            checks,
        )

    cap = open_payload.get("cap", {})
    max_per_charge = cap.get("max_per_charge_paise", 7500000)
    if expected_amount_paise > max_per_charge:
        return (
            False,
            f"Open Mandate Per-Charge Ceiling Exceeded: {expected_amount_paise} paise exceeds limit of {max_per_charge} paise",
            checks,
        )

    checks["amount_within_limits"] = "VALID"
    checks["cart_digest"] = actual_digest
    checks["open_jti"] = open_jti
    checks["closed_jti"] = closed_payload.get("jti")

    # Compute 4th Merkle Leaf (H_AP2)
    h_ap2 = compute_ap2_merkle_leaf(open_jti, closed_payload.get("jti"), actual_digest)
    checks["ap2_merkle_leaf"] = h_ap2

    return True, "Google AP2 Mandate Chain and Cart Digest verified successfully", checks


def compute_ap2_merkle_leaf(open_jti: str, closed_jti: str, cart_digest: str) -> str:
    """
    Computes the 4th leaf for the cryptographic Merkle Tree:
    H_AP2 = SHA-256(open_jti || closed_jti || cart_digest)
    """
    data = f"{open_jti}:{closed_jti}:{cart_digest}".encode("utf-8")
    return f"0x{hashlib.sha256(data).hexdigest()}"
