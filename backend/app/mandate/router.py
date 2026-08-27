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
