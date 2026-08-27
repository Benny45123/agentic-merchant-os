from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.commerce_agent.schemas import (
    ChatRequest,
    ChatResponse,
    CheckoutIntentRequest,
    CheckoutIntentResponse,
)
from app.commerce_agent.service import build_checkout_intent, chat
from app.core.auth import CurrentUser, get_current_user, get_optional_user
from app.core.db import get_session

router = APIRouter(prefix="/agent", tags=["Commerce Agent (Buyer Assistant)"])


@router.post("/chat", response_model=ChatResponse)
async def chat_turn(
    body: ChatRequest,
    session: AsyncSession = Depends(get_session),
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
):
    """
    Conversational buyer shopping interaction.
    Searches catalog, manages cart state, and provides safe recommendations.
    """
    buyer_id = current_user.sub if current_user and current_user.is_buyer else body.buyer_id
    return await chat(
        session_id=body.session_id,
        buyer_id=buyer_id,
        message=body.message,
        session=session,
    )


@router.post("/checkout-intent", response_model=CheckoutIntentResponse)
async def create_checkout_intent(
    body: CheckoutIntentRequest,
    session: AsyncSession = Depends(get_session),
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
):
    """
    Builds TransactionIntent deterministically from CartItem state and forwards to Guardian.
    """
    buyer_id = current_user.sub if current_user and current_user.is_buyer else body.buyer_id
    try:
        return await build_checkout_intent(
            session_id=body.session_id,
            buyer_id=buyer_id,
            merchant_id=body.merchant_id,
            session=session,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
