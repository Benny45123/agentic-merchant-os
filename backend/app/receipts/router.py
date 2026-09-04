from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user, get_optional_user
from app.core.db import get_session
from app.receipts.schemas import (
    ReceiptListResponse,
    ReceiptResponse,
    ReplayResponse,
)
from app.receipts.service import get_receipt, list_receipts, replay

router = APIRouter(prefix="/receipts", tags=["Receipts"])


@router.get("", response_model=ReceiptListResponse)
async def get_receipts_list(
    merchant_id: Optional[str] = Query(None, description="Merchant UUID filter"),
    buyer_id: Optional[str] = Query(None, description="Buyer UUID filter"),
    decision: Optional[str] = Query(None, description="Decision filter (APPROVE, BLOCK, REQUIRE_CONFIRMATION)"),
    from_date: Optional[datetime] = Query(None, alias="from", description="ISO start timestamp"),
    to_date: Optional[datetime] = Query(None, alias="to", description="ISO end timestamp"),
    limit: Optional[int] = Query(None, description="Max receipts to return"),
    session: AsyncSession = Depends(get_session),
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
):
    """Retrieve decision receipts matching filters."""
    receipts = await list_receipts(
        merchant_id=merchant_id,
        buyer_id=buyer_id,
        decision=decision,
        from_ts=from_date,
        to_ts=to_date,
        limit=limit,
        session=session,
    )
    return ReceiptListResponse(receipts=[ReceiptResponse.model_validate(r) for r in receipts])


@router.get("/{receipt_id}", response_model=ReceiptResponse)
async def get_single_receipt(
    receipt_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
):
    """Retrieve single receipt by ID."""
    receipt = await get_receipt(receipt_id, session)
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Receipt with ID '{receipt_id}' not found"
        )
    return ReceiptResponse.model_validate(receipt)


@router.post("/{receipt_id}/replay", response_model=ReplayResponse)
async def replay_receipt_decision(
    receipt_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
):
    """
    Deterministic audit replay of a historical receipt.
    Re-runs pure mandate and policy logic on frozen receipt snapshot data.
    """
    try:
        return await replay(receipt_id, session)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
