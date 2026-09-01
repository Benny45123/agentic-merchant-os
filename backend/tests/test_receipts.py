from datetime import datetime, timedelta
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import generate_uuid, utc_now
from app.core.enums import DecisionType
from app.guardian.pipeline import evaluate_transaction_intent
from app.guardian.schemas import IntentItemSchema, TransactionIntentRequest
from app.models import Receipt, Mandate
from app.receipts.service import get_receipt, list_receipts, replay

from app.seed import DEMO_BUYER_ID, DEMO_MERCHANT_ID, seed_data


import pytest_asyncio

@pytest_asyncio.fixture(autouse=True)
async def setup_seed(test_db_session: AsyncSession):
    await seed_data(test_db_session)


@pytest.mark.asyncio
async def test_receipt_creation_and_deterministic_replay(test_db_session: AsyncSession):
    now = utc_now()

    # 1. Generate an APPROVED transaction
    req_approve = TransactionIntentRequest(
        intent_id=generate_uuid(),
        buyer_id=DEMO_BUYER_ID,
        merchant_id=DEMO_MERCHANT_ID,
        items=[
            IntentItemSchema(
                sku="HP-001",
                qty=1,
                observed_price=449900,
                catalog_version=17,
                snapshot_id="snap_hp001_v17",
            )
        ],
        requested_discount_pct=0,
        created_at=now,
        expires_at=now + timedelta(minutes=2),
    )
    resp_approve = await evaluate_transaction_intent(req_approve, test_db_session)
    assert resp_approve.decision == DecisionType.APPROVE
    assert resp_approve.receipt_id != ""

    # Replay the approved receipt
    replay_approve = await replay(resp_approve.receipt_id, test_db_session)
    assert replay_approve.matches_original is True
    assert replay_approve.replay_decision == "APPROVE"

    # 2. Generate a BLOCKED transaction (exceeding mandate limit)
    stmt = select(Mandate).where(Mandate.buyer_id == DEMO_BUYER_ID, Mandate.active == True)
    res = await test_db_session.execute(stmt)
    mandate = res.scalar_one_or_none()
    if mandate:
        mandate.max_amount = 1000000  # ₹10,000.00 ceiling
        await test_db_session.commit()

    req_block = TransactionIntentRequest(
        intent_id=generate_uuid(),
        buyer_id=DEMO_BUYER_ID,
        merchant_id=DEMO_MERCHANT_ID,
        items=[
            IntentItemSchema(
                sku="SPK-001",
                qty=5,  # 5 * 899900 = 4499500 (> 1000000 max amount)
                observed_price=899900,
                catalog_version=1,
                snapshot_id=None,
            )
        ],
        requested_discount_pct=0,
        created_at=now,
        expires_at=now + timedelta(minutes=2),
    )
    resp_block = await evaluate_transaction_intent(req_block, test_db_session)
    assert resp_block.decision == DecisionType.BLOCK


    # Replay the blocked receipt
    replay_block = await replay(resp_block.receipt_id, test_db_session)
    assert replay_block.matches_original is True
    assert replay_block.replay_decision == "BLOCK"

    # 3. Test list_receipts filter
    all_receipts = await list_receipts(merchant_id=DEMO_MERCHANT_ID, session=test_db_session)
    assert len(all_receipts) >= 2

    blocked_receipts = await list_receipts(
        merchant_id=DEMO_MERCHANT_ID,
        decision="BLOCK",
        session=test_db_session,
    )
    assert len(blocked_receipts) >= 1
    assert all(r.decision == DecisionType.BLOCK for r in blocked_receipts)
