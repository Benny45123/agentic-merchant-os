from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.guardian.pipeline import (
    confirm_guardian_decision,
    evaluate_campaign_proposal,
    evaluate_transaction_intent,
)
from app.guardian.schemas import (
    CampaignProposalRequest,
    GuardianDecisionResponse,
    TransactionIntentRequest,
)

router = APIRouter(prefix="/guardian", tags=["Guardian (Deterministic Policy Engine)"])


@router.post("/evaluate", response_model=GuardianDecisionResponse)
async def evaluate_intent(
    body: TransactionIntentRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Internal evaluation of TransactionIntent against buyer mandate & merchant policy.
    Zero LLM calls. Deterministic gate to Razorpay order creation.
    """
    return await evaluate_transaction_intent(body, session)


@router.post("/evaluate_campaign", response_model=GuardianDecisionResponse)
async def evaluate_campaign(
    body: CampaignProposalRequest,
    session: AsyncSession = Depends(get_session),
):
    """Internal validation of campaign proposal against merchant policy."""
    return await evaluate_campaign_proposal(body, session)


@router.post("/confirm/{decision_id}", response_model=GuardianDecisionResponse)
async def confirm_decision(
    decision_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Re-evaluates fresh state for a decision that previously required confirmation.
    """
    try:
        return await confirm_guardian_decision(decision_id, session)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
