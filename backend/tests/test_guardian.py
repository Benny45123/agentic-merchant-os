from datetime import datetime, timezone, timedelta
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.base import generate_uuid, utc_now
from app.core.enums import DecisionType
from app.guardian.pipeline import (
    evaluate_campaign_proposal,
    evaluate_transaction_intent,
)
from app.guardian.schemas import (
    CampaignProposalRequest,
    IntentItemSchema,
    TransactionIntentRequest,
)
from app.mandate.schemas import MandateCreate
from app.mandate.service import create_mandate
from app.models import Product, Mandate

from app.policy.schemas import MerchantPolicyUpdate
from app.policy.service import update_policy
from app.seed import DEMO_BUYER_ID, DEMO_MERCHANT_ID, seed_data


import pytest_asyncio

@pytest_asyncio.fixture(autouse=True)
async def setup_seed(test_db_session: AsyncSession):
    await seed_data(test_db_session)


def make_intent_req(
    sku: str = "HP-001",
    qty: int = 1,
    observed_price: int = 449900,
    requested_discount: int = 0,
    buyer_id: str = DEMO_BUYER_ID,
    merchant_id: str = DEMO_MERCHANT_ID,
    expires_in_seconds: int = 120,
    intent_id: str = None,
) -> TransactionIntentRequest:
    now = utc_now()
    return TransactionIntentRequest(
        intent_id=intent_id or generate_uuid(),
        buyer_id=buyer_id,
        merchant_id=merchant_id,
        items=[
            IntentItemSchema(
                sku=sku,
                qty=qty,
                observed_price=observed_price,
                catalog_version=17,
                snapshot_id="snap_test",
            )
        ],
        requested_discount_pct=requested_discount,
        created_at=now,
        expires_at=now + timedelta(seconds=expires_in_seconds),
    )


@pytest.mark.asyncio
async def test_case_01_valid_intent_approves(test_db_session: AsyncSession):
    """Case 1: Valid intent within mandate & policy -> APPROVE"""
    req = make_intent_req()
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.APPROVE
    assert resp.final_verified_total == 449900
    assert resp.razorpay_order is not None
    assert resp.receipt_id != ""


@pytest.mark.asyncio
async def test_case_02_quantity_exceeds_mandate(test_db_session: AsyncSession):
    """Case 2: Quantity exceeds mandate.max_quantity_per_item (5) -> BLOCK"""
    req = make_intent_req(qty=6)
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.BLOCK
    assert "exceeds mandate limit" in resp.primary_reason


@pytest.mark.asyncio
async def test_case_03_category_not_in_mandate(test_db_session: AsyncSession):
    """Case 3: Category not in mandate.allowed_categories -> BLOCK"""
    # Create product with forbidden category 'luxury'
    p = Product(
        sku="LUX-001",
        merchant_id=DEMO_MERCHANT_ID,
        name="Gold Watch",
        category="luxury",
        price=50000,
        currency="INR",
        inventory=10,
        description="Luxury gold watch",
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    test_db_session.add(p)
    await test_db_session.flush()

    req = make_intent_req(sku="LUX-001", observed_price=50000)
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.BLOCK
    assert "Category" in resp.primary_reason or "not authorized" in resp.primary_reason


@pytest.mark.asyncio
async def test_case_04_merchant_not_in_mandate(test_db_session: AsyncSession):
    """Case 4: Merchant not in mandate.allowed_merchants -> BLOCK"""
    req = make_intent_req(merchant_id="unauthorized_merchant_999")
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.BLOCK
    assert "not authorized by buyer mandate" in resp.primary_reason


@pytest.mark.asyncio
async def test_case_05_total_exceeds_mandate_max(test_db_session: AsyncSession):
    """Case 5: Total exceeds mandate.max_amount (1000000 paise / ₹10,000) -> BLOCK"""
    stmt = select(Mandate).where(Mandate.buyer_id == DEMO_BUYER_ID, Mandate.active == True)
    res = await test_db_session.execute(stmt)
    mandate = res.scalar_one_or_none()
    mandate.max_amount = 1000000  # ₹10,000.00
    await test_db_session.commit()

    # 3 units of SPK-001 @ 899900 = 2699700 (> 1000000)
    req = make_intent_req(sku="SPK-001", qty=3, observed_price=899900)
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.BLOCK
    assert "exceed" in resp.primary_reason or "spending limit" in resp.primary_reason or "ceiling" in resp.primary_reason



@pytest.mark.asyncio
async def test_case_06_confirmation_required_above_threshold(test_db_session: AsyncSession):
    """Case 6: Total exceeds confirmation_required_above (500000) but under max_amount (10000000) -> REQUIRE_CONFIRMATION"""
    stmt = select(Mandate).where(Mandate.buyer_id == DEMO_BUYER_ID, Mandate.active == True)
    res = await test_db_session.execute(stmt)
    mandate = res.scalar_one_or_none()
    mandate.confirmation_required_above = 500000  # ₹5,000.00
    await test_db_session.commit()

    # 1 unit of WCH-001 @ 649900 (> 500000 threshold, < 10000000 max)
    req = make_intent_req(sku="WCH-001", qty=1, observed_price=649900)
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.REQUIRE_CONFIRMATION



@pytest.mark.asyncio
async def test_case_07_total_exceeds_policy_max_order_value(test_db_session: AsyncSession):
    """Case 7: Total exceeds policy.maximum_order_value (10000000 paise / ₹1 Lakh) -> BLOCK"""
    # Temporarily raise mandate max amount so mandate passes, but policy blocks at ₹1 Lakh
    await create_mandate(
        DEMO_BUYER_ID,
        MandateCreate(
            max_amount=20000000,
            max_quantity_per_item=10,
            currency="INR",
            expires_at=utc_now() + timedelta(days=30),
        ),
        test_db_session,
    )
    req = make_intent_req(sku="PHN-APL-15", qty=2, observed_price=6990000)  # Total 13980000 > 10000000 (₹1.39 Lakhs > ₹1 Lakh)
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.BLOCK
    assert "maximum order value" in resp.primary_reason



@pytest.mark.asyncio
async def test_case_08_discount_exceeds_policy_max(test_db_session: AsyncSession):
    """Case 8: Discount exceeds policy.maximum_discount_pct (20%) -> BLOCK"""
    req = make_intent_req(requested_discount=25)
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.BLOCK
    assert "Discount of 25% exceeds" in resp.primary_reason


@pytest.mark.asyncio
async def test_case_09_margin_below_policy_minimum(test_db_session: AsyncSession):
    """Case 9: Resulting margin below policy.minimum_margin_pct (15%) -> BLOCK"""
    # HP-001 price 449900, cost 300000. If 15% discount applied, price_after = 382415, margin = 21.5% (ok)
    # If we apply 20% discount: price_after = 359920, cost = 300000, margin = (59920/359920)*100 = 16.6%
    # Update policy to require 18% min margin:
    await update_policy(
        DEMO_MERCHANT_ID,
        MerchantPolicyUpdate(
            maximum_discount_pct=25,
            minimum_margin_pct=18,
            maximum_order_value=2000000,
            minimum_stock_to_sell=2,
        ),
        test_db_session,
    )
    req = make_intent_req(requested_discount=20)
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.BLOCK
    assert "margin" in resp.primary_reason.lower()


@pytest.mark.asyncio
async def test_case_10_inventory_below_policy_reserve(test_db_session: AsyncSession):
    """Case 10: Resulting inventory below policy.minimum_stock_to_sell -> BLOCK"""
    # Set reserve to 8 units. ATTACK-SKU-001 has inventory 10. Requesting 3 leaves 7 < 8 -> BLOCK on reserve
    await update_policy(
        DEMO_MERCHANT_ID,
        MerchantPolicyUpdate(
            maximum_discount_pct=20,
            minimum_margin_pct=15,
            maximum_order_value=2000000,
            minimum_stock_to_sell=8,
        ),
        test_db_session,
    )
    req = make_intent_req(sku="ATTACK-SKU-001", qty=3, observed_price=399900)
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.BLOCK
    assert "minimum stock" in resp.primary_reason.lower() or "reserve" in resp.primary_reason.lower()


@pytest.mark.asyncio
async def test_case_11_price_increased_mid_flow(test_db_session: AsyncSession):
    """Case 11: Price increased since snapshot -> REQUIRE_CONFIRMATION"""
    # Intent saw observed_price 400000, but authoritative is 449900
    req = make_intent_req(observed_price=400000)
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.REQUIRE_CONFIRMATION
    assert "price increased" in resp.checks[3].detail.lower() or any("increased" in c.detail for c in resp.checks)


@pytest.mark.asyncio
async def test_case_12_price_decreased_mid_flow(test_db_session: AsyncSession):
    """Case 12: Price decreased since snapshot -> APPROVE at lower authoritative price"""
    # Intent saw observed_price 480000, but authoritative is 449900
    req = make_intent_req(observed_price=480000)
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.APPROVE
    assert resp.final_verified_total == 449900


@pytest.mark.asyncio
async def test_case_13_insufficient_inventory(test_db_session: AsyncSession):
    """Case 13: Requested quantity > total inventory -> BLOCK"""
    req = make_intent_req(sku="SPK-001", qty=20, observed_price=899900)  # SPK-001 has 15
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.BLOCK
    assert "Insufficient inventory" in resp.primary_reason or "exceeds" in resp.primary_reason


@pytest.mark.asyncio
async def test_case_14_product_no_longer_exists(test_db_session: AsyncSession):
    """Case 14: Product no longer exists -> BLOCK"""
    req = make_intent_req(sku="NON_EXISTENT_SKU_999")
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.BLOCK
    assert "no longer exists" in resp.primary_reason


@pytest.mark.asyncio
async def test_case_15_expired_intent(test_db_session: AsyncSession):
    """Case 15: Expired intent -> BLOCK"""
    req = make_intent_req(expires_in_seconds=-10)
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.BLOCK
    assert "expired" in resp.primary_reason.lower()


@pytest.mark.asyncio
async def test_case_16_duplicate_intent_id(test_db_session: AsyncSession):
    """Case 16: Duplicate intent_id -> second call BLOCK"""
    dup_id = generate_uuid()
    req1 = make_intent_req(intent_id=dup_id)
    resp1 = await evaluate_transaction_intent(req1, test_db_session)
    assert resp1.decision == DecisionType.APPROVE

    req2 = make_intent_req(intent_id=dup_id)
    resp2 = await evaluate_transaction_intent(req2, test_db_session)
    assert resp2.decision == DecisionType.BLOCK
    assert "Duplicate" in resp2.primary_reason


@pytest.mark.asyncio
async def test_case_17_no_active_mandate(test_db_session: AsyncSession):
    """Case 17: No active mandate -> BLOCK"""
    req = make_intent_req(buyer_id="buyer_without_mandate_007")
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.BLOCK
    assert "No active mandate" in resp.primary_reason


@pytest.mark.asyncio
async def test_case_18_expired_mandate(test_db_session: AsyncSession):
    """Case 18: Expired mandate -> BLOCK"""
    # Create expired mandate
    await create_mandate(
        DEMO_BUYER_ID,
        MandateCreate(
            max_amount=1000000,
            currency="INR",
            expires_at=utc_now() - timedelta(days=1),
        ),
        test_db_session,
    )
    req = make_intent_req()
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.BLOCK
    assert "mandate" in resp.primary_reason.lower()


@pytest.mark.asyncio
async def test_case_19_suspicious_content_flag_informational_only(test_db_session: AsyncSession):
    """Case 19: suspicious_content_flag=true on SKU with valid intent -> APPROVE still (informational only)"""
    req = make_intent_req(sku="ATTACK-SKU-001", qty=1, observed_price=399900)
    resp = await evaluate_transaction_intent(req, test_db_session)
    assert resp.decision == DecisionType.APPROVE
    # Check that security flag is noted in receipt check detail
    flag_check = next((c for c in resp.checks if c.name == "security.catalog_content_flagged"), None)
    assert flag_check is not None
    assert "FLAGGED" in flag_check.detail


@pytest.mark.asyncio
async def test_case_20_campaign_proposal_exceeding_discount_ceiling(test_db_session: AsyncSession):
    """Case 20: Campaign proposal exceeding allowed_campaign_discount_pct (15%) -> BLOCK"""
    now = utc_now()
    prop_req = CampaignProposalRequest(
        proposal_id=generate_uuid(),
        merchant_id=DEMO_MERCHANT_ID,
        objective="Massive 50% liquidation",
        eligible_skus=["HP-001"],
        discount_pct=50,
        budget=1000000,
        starts_at=now,
        ends_at=now + timedelta(days=7),
        rationale="Clear stock fast",
    )
    resp = await evaluate_campaign_proposal(prop_req, test_db_session)
    assert resp.decision == DecisionType.BLOCK
    assert "exceeds" in resp.primary_reason


@pytest.mark.asyncio
async def test_case_21_campaign_proposal_exceeding_daily_budget_cap(test_db_session: AsyncSession):
    """Case 21: Campaign proposal exceeding daily_campaign_budget_cap (5000000 paise) -> REQUIRE_CONFIRMATION"""
    now = utc_now()
    prop_req = CampaignProposalRequest(
        proposal_id=generate_uuid(),
        merchant_id=DEMO_MERCHANT_ID,
        objective="Large scale weekend promotion",
        eligible_skus=["HP-001"],
        discount_pct=10,
        budget=10000000,  # 10M > 5M cap
        starts_at=now,
        ends_at=now + timedelta(days=7),
        rationale="Scale up budget for weekend",
    )
    resp = await evaluate_campaign_proposal(prop_req, test_db_session)
    assert resp.decision == DecisionType.REQUIRE_CONFIRMATION
