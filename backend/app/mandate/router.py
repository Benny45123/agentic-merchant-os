from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user, get_optional_user
from app.core.db import get_session
from app.mandate.schemas import MandateCreate, MandateSchema
from app.mandate.service import create_mandate, get_active_mandate

router = APIRouter(prefix="/mandate", tags=["Mandate"])


@router.get("/active", response_model=MandateSchema)
async def get_active_buyer_mandate(
    buyer_id: str = Query(..., description="Target buyer UUID"),
    session: AsyncSession = Depends(get_session),
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
):
    """Retrieve active mandate for a buyer."""
    mandate = await get_active_mandate(buyer_id, session)
    if not mandate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active mandate found for buyer '{buyer_id}'"
        )
    return MandateSchema.model_validate(mandate)


@router.post("", response_model=MandateSchema, status_code=status.HTTP_201_CREATED)
async def set_buyer_mandate(
    data: MandateCreate,
    buyer_id: Optional[str] = Query(None, description="Buyer ID if not authenticated via token"),
    session: AsyncSession = Depends(get_session),
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
):
    """Declare or update buyer mandate."""
    target_buyer_id = current_user.sub if current_user and current_user.is_buyer else (buyer_id or "b_001")
    mandate = await create_mandate(target_buyer_id, data, session)
    return MandateSchema.model_validate(mandate)


@router.get("/ap2/open/{buyer_id}")
async def get_google_ap2_open_mandate(
    buyer_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Retrieve or mint the Google AP2 Open Mandate JWT for a buyer.
    Adheres to the official Google Agent Payments Protocol (ES256 / NIST P-256).
    """
    from app.mandate.ap2_service import mint_open_mandate, get_or_create_buyer_keypair, get_or_create_agent_keypair

    mandate = await get_active_mandate(buyer_id, session)
    if mandate and mandate.open_mandate_jwt:
        return {
            "status": "ACTIVE",
            "buyer_id": buyer_id,
            "open_mandate_jwt": mandate.open_mandate_jwt,
            "user_public_key_pem": mandate.user_public_key_pem,
            "max_total_paise": mandate.max_amount,
            "max_per_charge_paise": getattr(mandate, "max_amount_per_charge", 7500000),
            "autopay_token": mandate.autopay_token,
        }

    # Mint a fresh Open Mandate JWT
    priv_pem, pub_pem = get_or_create_buyer_keypair(buyer_id)
    token, pub_key = mint_open_mandate(
        buyer_id=buyer_id,
        max_total_paise=mandate.max_amount if mandate else 10000000,
        max_per_charge_paise=getattr(mandate, "max_amount_per_charge", 7500000) if mandate else 5000000,
        autopay_token=mandate.autopay_token if mandate else None,
        customer_id=getattr(mandate, "customer_id", None) if mandate else None,
        user_private_key_pem=priv_pem,
    )

    if mandate:
        mandate.open_mandate_jwt = token
        mandate.user_public_key_pem = pub_key
        await session.commit()

    return {
        "status": "MINTED",
        "buyer_id": buyer_id,
        "open_mandate_jwt": token,
        "user_public_key_pem": pub_key,
        "max_total_paise": mandate.max_amount if mandate else 10000000,
        "max_per_charge_paise": getattr(mandate, "max_amount_per_charge", 7500000) if mandate else 5000000,
        "autopay_token": mandate.autopay_token if mandate else None,
    }


@router.post("/ap2/mint-closed")
async def mint_google_ap2_closed_mandate(
    data: dict,
    session: AsyncSession = Depends(get_session),
):
    """
    Mints a transaction-specific Google AP2 Closed Mandate JWT binding the canonical cart digest.
    """
    from app.mandate.ap2_service import mint_closed_mandate, mint_open_mandate, get_or_create_agent_keypair

    buyer_id = data.get("buyer_id", "b_001")
    items = data.get("items", [])
    amount_paise = data.get("amount_paise", 0)
    intent_id = data.get("intent_id")
    open_jwt = data.get("open_mandate_jwt")

    if not open_jwt:
        mandate = await get_active_mandate(buyer_id, session)
        if mandate and mandate.open_mandate_jwt:
            open_jwt = mandate.open_mandate_jwt
        else:
            open_jwt, _ = mint_open_mandate(buyer_id=buyer_id)

    closed_jwt, agent_pub = mint_closed_mandate(
        open_mandate_jwt=open_jwt,
        items=items,
        amount_paise=amount_paise,
        intent_id=intent_id,
    )

    return {
        "closed_mandate_jwt": closed_jwt,
        "agent_public_key_pem": agent_pub,
        "open_mandate_jwt": open_jwt,
    }


@router.post("/ap2/verify-chain")
async def verify_google_ap2_mandate_chain(
    data: dict,
):
    """
    Deterministic 6-point verification gate for Google AP2 Open vs. Closed Mandate chains.
    """
    from app.mandate.ap2_service import verify_ap2_mandate_chain

    open_jwt = data.get("open_mandate_jwt")
    closed_jwt = data.get("closed_mandate_jwt")
    items = data.get("items", [])
    amount_paise = data.get("amount_paise", 0)
    user_pub = data.get("user_public_key_pem")
    agent_pub = data.get("agent_public_key_pem")

    if not open_jwt or not closed_jwt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both open_mandate_jwt and closed_mandate_jwt are required for AP2 chain verification",
        )

    is_valid, reason, checks = verify_ap2_mandate_chain(
        open_mandate_jwt=open_jwt,
        closed_mandate_jwt=closed_jwt,
        expected_items=items,
        expected_amount_paise=amount_paise,
        user_public_key_pem=user_pub,
        agent_public_key_pem=agent_pub,
    )

    return {
        "valid": is_valid,
        "reason": reason,
        "checks": checks,
    }

