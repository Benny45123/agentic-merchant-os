from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.negotiation.schemas import (
    RFQRequest,
    RFQResponse,
    AcceptOfferRequest,
    NegotiationSettlementResponse,
)
from app.negotiation.service import process_commerce_rfq, settle_negotiated_offer

router = APIRouter(prefix="/commerce", tags=["Autonomous A2A Dynamic Negotiation"])


@router.post("/rfq", response_model=RFQResponse)
async def submit_rfq(
    body: RFQRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Autonomous Request for Quote (RFQ) Endpoint.
    Allows an external AI Buyer Agent to propose a custom volume/unit price.
    The Merchant Pricing Agent calculates margin boundaries and returns bilateral counter-offers.
    """
    try:
        return await process_commerce_rfq(body, session)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RFQ evaluation error: {str(e)}",
        )


@router.post("/accept", response_model=NegotiationSettlementResponse)
async def accept_and_settle_offer(
    body: AcceptOfferRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Accepts a negotiated counter-offer (Direct Price or Bundle Sweetener).
    Transforms the agreement into a TransactionIntent, executes deterministic Guardian validation,
    and produces a Razorpay test order + Decision Receipt.
    """
    try:
        return await settle_negotiated_offer(body, session)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Settlement error: {str(e)}",
        )
