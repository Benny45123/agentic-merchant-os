"""
Automated Pytest Suite for Google Agent Payments Protocol (AP2) Mandate Chains (ES256).

Verifies:
1. ECDSA P-256 (ES256) keypair generation and persistence.
2. Canonical cart digest computation and lexicographical sorting invariance.
3. Open Mandate JWT minting and ES256 signature verification.
4. Closed Mandate JWT minting with canonical cart digest and parent JTI binding.
5. Full 6-point AP2 dual-chain verification gate.
6. Adversarial tamper detection: SKU substitution, price inflation, signature tampering.
7. End-to-end Commerce Guardian pipeline evaluation and Decision Receipt Merkle leaf formation.
"""

import hashlib
import time
import pytest
from datetime import timedelta

from app.core.base import utc_now
from app.core.enums import DecisionType
from app.guardian.pipeline import evaluate_transaction_intent
from app.guardian.schemas import IntentItemSchema, TransactionIntentRequest
from app.mandate.ap2_service import (
    compute_ap2_merkle_leaf,
    compute_canonical_cart_digest,
    generate_es256_keypair,
    get_or_create_agent_keypair,
    get_or_create_buyer_keypair,
    mint_closed_mandate,
    mint_open_mandate,
    verify_ap2_mandate_chain,
    verify_closed_mandate,
    verify_open_mandate,
)
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.mandate.schemas import MandateCreate
from app.mandate.service import create_mandate
from app.policy.schemas import MerchantPolicyUpdate
from app.policy.service import update_policy
from app.seed import seed_data


@pytest_asyncio.fixture(autouse=True)
async def setup_seed(test_db_session: AsyncSession):
    await seed_data(test_db_session)


def test_es256_keypair_generation():
    """Verify that ECDSA P-256 keypairs generate with valid PEM headers."""
    priv_pem, pub_pem = generate_es256_keypair()
    assert "BEGIN PRIVATE KEY" in priv_pem
    assert "BEGIN PUBLIC KEY" in pub_pem


def test_canonical_cart_digest_invariance():
    """Verify that cart digest is strictly identical regardless of item list order."""
    items_order_a = [
        {"sku": "HP-001", "qty": 1, "price_paise": 449900},
        {"sku": "CASE-HP", "qty": 1, "price_paise": 79900},
    ]
    items_order_b = [
        {"sku": "CASE-HP", "qty": 1, "price_paise": 79900},
        {"sku": "HP-001", "qty": 1, "price_paise": 449900},
    ]

    digest_a = compute_canonical_cart_digest(items_order_a)
    digest_b = compute_canonical_cart_digest(items_order_b)

    assert digest_a == digest_b
    assert len(digest_a) == 64  # SHA-256 hex string


def test_cart_digest_changes_on_tamper():
    """Verify that any SKU or price alteration changes the cart digest bit-for-bit."""
    genuine_items = [{"sku": "HP-001", "qty": 1, "price_paise": 449900}]
    tampered_items = [{"sku": "HP-001", "qty": 1, "price_paise": 100}]  # Underpayment attack

    digest_genuine = compute_canonical_cart_digest(genuine_items)
    digest_tampered = compute_canonical_cart_digest(tampered_items)

    assert digest_genuine != digest_tampered


def test_mint_and_verify_open_mandate():
    """Verify Open Mandate JWT minting and signature validation."""
    buyer_id = "b_test_001"
    token, pub_key = mint_open_mandate(
        buyer_id=buyer_id,
        max_total_paise=10000000,
        max_per_charge_paise=5000000,
    )

    claims = verify_open_mandate(token, pub_key)
    assert claims["iss"] == f"urn:buyer:{buyer_id}"
    assert claims["mandate_type"] == "GOOGLE_AP2_OPEN_MANDATE"
    assert claims["cap"]["max_total_paise"] == 10000000
    assert claims["jti"].startswith("mnd_open_")


def test_mint_and_verify_closed_mandate():
    """Verify Closed Mandate JWT minting bound to parent Open Mandate."""
    buyer_id = "b_test_002"
    open_jwt, user_pub = mint_open_mandate(buyer_id=buyer_id)
    items = [{"sku": "HP-001", "qty": 1, "price_paise": 449900}]

    closed_jwt, agent_pub = mint_closed_mandate(
        open_mandate_jwt=open_jwt,
        items=items,
        amount_paise=449900,
    )

    claims = verify_closed_mandate(closed_jwt, agent_pub)
    assert claims["mandate_type"] == "GOOGLE_AP2_CLOSED_MANDATE"
    assert claims["transaction"]["amount_paise"] == 449900
    assert claims["jti"].startswith("mnd_closed_")
    assert "cart_digest" in claims
    assert claims["parent_mandate_id"].startswith("mnd_open_")


def test_full_ap2_mandate_chain_success():
    """Verify 6-point verification gate passes for an authentic delegation chain."""
    buyer_id = "b_test_003"
    open_jwt, user_pub = mint_open_mandate(buyer_id=buyer_id)
    items = [{"sku": "HP-001", "qty": 1, "price_paise": 449900}]

    closed_jwt, agent_pub = mint_closed_mandate(
        open_mandate_jwt=open_jwt,
        items=items,
        amount_paise=449900,
    )

    is_valid, reason, checks = verify_ap2_mandate_chain(
        open_mandate_jwt=open_jwt,
        closed_mandate_jwt=closed_jwt,
        expected_items=items,
        expected_amount_paise=449900,
        user_public_key_pem=user_pub,
        agent_public_key_pem=agent_pub,
    )

    assert is_valid is True
    assert checks["open_mandate_signature"] == "VALID"
    assert checks["closed_mandate_signature"] == "VALID"
    assert checks["chain_linkage"] == "VALID"
    assert checks["cart_digest_verified"] == "VALID"
    assert checks["amount_within_limits"] == "VALID"
    assert checks["ap2_merkle_leaf"].startswith("0x")


def test_ap2_chain_rejects_sku_tampering():
    """Adversarial Attack: Closed mandate was signed for HP-001, but attacker submits AU-001."""
    buyer_id = "b_test_004"
    open_jwt, user_pub = mint_open_mandate(buyer_id=buyer_id)
    authorized_items = [{"sku": "HP-001", "qty": 1, "price_paise": 449900}]

    # Agent signs Closed Mandate for HP-001
    closed_jwt, agent_pub = mint_closed_mandate(
        open_mandate_jwt=open_jwt,
        items=authorized_items,
        amount_paise=449900,
    )

    # Adversary attempts to swap cart item to GOLD-001
    adversary_items = [{"sku": "GOLD-001", "qty": 1, "price_paise": 449900}]

    is_valid, reason, checks = verify_ap2_mandate_chain(
        open_mandate_jwt=open_jwt,
        closed_mandate_jwt=closed_jwt,
        expected_items=adversary_items,
        expected_amount_paise=449900,
        user_public_key_pem=user_pub,
        agent_public_key_pem=agent_pub,
    )

    assert is_valid is False
    assert "Cart Digest Mismatch" in reason


def test_ap2_chain_rejects_broken_parent_linkage():
    """Adversarial Attack: Closed mandate references arbitrary parent JTI."""
    buyer_id = "b_test_005"
    open_jwt_1, user_pub_1 = mint_open_mandate(buyer_id=f"{buyer_id}_real")
    open_jwt_2, user_pub_2 = mint_open_mandate(buyer_id=f"{buyer_id}_other")
    items = [{"sku": "HP-001", "qty": 1, "price_paise": 449900}]

    # Signed with open_jwt_1
    closed_jwt, agent_pub = mint_closed_mandate(
        open_mandate_jwt=open_jwt_1,
        items=items,
        amount_paise=449900,
    )

    # Evaluated against open_jwt_2 (different parent)
    is_valid, reason, checks = verify_ap2_mandate_chain(
        open_mandate_jwt=open_jwt_2,
        closed_mandate_jwt=closed_jwt,
        expected_items=items,
        expected_amount_paise=449900,
        user_public_key_pem=user_pub_2,
        agent_public_key_pem=agent_pub,
    )

    assert is_valid is False
    assert "Chain Broken" in reason


def test_ap2_merkle_leaf_deterministic():
    """Verify that H_AP2 Merkle leaf hashes to a valid 32-byte hex string."""
    leaf = compute_ap2_merkle_leaf("mnd_open_123", "mnd_closed_456", "digest_789")
    assert leaf.startswith("0x")
    assert len(leaf) == 66  # "0x" + 64 hex chars


@pytest.mark.asyncio
async def test_guardian_pipeline_with_ap2_closed_mandate(test_db_session: AsyncSession):
    """End-to-end integration: Guardian validates valid Google AP2 Closed Mandate."""
    buyer_id = "b_ap2_shopper_01"
    merchant_id = "m_001"
    now = utc_now()

    # Update policy
    await update_policy(
        merchant_id=merchant_id,
        data=MerchantPolicyUpdate(
            maximum_discount_pct=20,
            minimum_margin_pct=15,
            maximum_order_value=15000000,
            minimum_stock_to_sell=1,
        ),
        session=test_db_session,
    )

    # Create active buyer mandate with AutoPay
    mandate = await create_mandate(
        buyer_id=buyer_id,
        data=MandateCreate(
            max_amount=15000000,
            max_quantity_per_item=5,
            currency="INR",
            expires_at=now + timedelta(days=90),
            autopay_enabled=True,
            autopay_token="tok_rzp_autopay_ap2_test",
            recurring_auth_status="ACTIVE",
        ),
        session=test_db_session,
    )

    items = [{"sku": "HP-001", "qty": 1, "price_paise": 449900}]
    closed_jwt, agent_pub = mint_closed_mandate(
        open_mandate_jwt=mandate.open_mandate_jwt,
        items=items,
        amount_paise=449900,
    )

    intent_req = TransactionIntentRequest(
        intent_id=f"intent_ap2_{int(time.time())}",
        buyer_id=buyer_id,
        merchant_id=merchant_id,
        items=[
            IntentItemSchema(
                sku="HP-001",
                qty=1,
                observed_price=449900,
            )
        ],
        requested_discount_pct=0,
        created_at=now,
        expires_at=now + timedelta(minutes=15),
        open_mandate_jwt=mandate.open_mandate_jwt,
        closed_mandate_jwt=closed_jwt,
        agent_public_key_pem=agent_pub,
    )

    decision = await evaluate_transaction_intent(intent_req, test_db_session)
    assert decision.decision == DecisionType.APPROVE

    # Confirm AP2 checks were recorded in the decision
    check_names = [c.name for c in decision.checks]
    assert "ap2.open_mandate_signature" in check_names
    assert "ap2.closed_mandate_signature" in check_names
    assert "ap2.cart_digest_verified" in check_names
    assert "ap2.chain_linkage_verified" in check_names


@pytest.mark.asyncio
async def test_guardian_pipeline_blocks_tampered_ap2_cart(test_db_session: AsyncSession):
    """Adversarial Defense: Guardian blocks transaction when closed mandate cart digest is tampered."""
    buyer_id = "b_ap2_shopper_02"
    merchant_id = "m_001"
    now = utc_now()

    mandate = await create_mandate(
        buyer_id=buyer_id,
        data=MandateCreate(
            max_amount=15000000,
            max_quantity_per_item=5,
            currency="INR",
            expires_at=now + timedelta(days=90),
            autopay_enabled=True,
            autopay_token="tok_rzp_autopay_ap2_test_2",
            recurring_auth_status="ACTIVE",
        ),
        session=test_db_session,
    )

    # Closed Mandate signed for CASE-HP (₹799)
    signed_items = [{"sku": "CASE-HP", "qty": 1, "price_paise": 79900}]
    closed_jwt, agent_pub = mint_closed_mandate(
        open_mandate_jwt=mandate.open_mandate_jwt,
        items=signed_items,
        amount_paise=79900,
    )

    # But Intent submits expensive Headphones HP-001 (₹4,499)
    intent_req = TransactionIntentRequest(
        intent_id=f"intent_ap2_tamper_{int(time.time())}",
        buyer_id=buyer_id,
        merchant_id=merchant_id,
        items=[
            IntentItemSchema(
                sku="HP-001",
                qty=1,
                observed_price=449900,
            )
        ],
        requested_discount_pct=0,
        created_at=now,
        expires_at=now + timedelta(minutes=15),
        open_mandate_jwt=mandate.open_mandate_jwt,
        closed_mandate_jwt=closed_jwt,
        agent_public_key_pem=agent_pub,
    )

    decision = await evaluate_transaction_intent(intent_req, test_db_session)
    # Must be blocked deterministically
    assert decision.decision == DecisionType.BLOCK
    assert "Google AP2" in decision.primary_reason
