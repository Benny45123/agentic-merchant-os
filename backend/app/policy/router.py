from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user, get_optional_user
from app.core.db import get_session
from app.policy.schemas import MerchantPolicySchema, MerchantPolicyUpdate
from app.policy.service import get_active_policy, update_policy

router = APIRouter(prefix="/policy", tags=["Policy"])


@router.get("", response_model=MerchantPolicySchema)
async def get_merchant_policy(
    merchant_id: str = Query(..., description="Merchant UUID"),
    session: AsyncSession = Depends(get_session),
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
):
    """Retrieve active versioned policy for a merchant."""
    policy = await get_active_policy(merchant_id, session)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No policy found for merchant '{merchant_id}'"
        )
    return MerchantPolicySchema.model_validate(policy)


@router.put("", response_model=MerchantPolicySchema)
async def put_merchant_policy(
    data: MerchantPolicyUpdate,
    merchant_id: Optional[str] = Query(None, description="Merchant ID if not in token"),
    session: AsyncSession = Depends(get_session),
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
):
    """Create a new version of the merchant policy."""
    target_merchant_id = current_user.sub if current_user and current_user.is_merchant else (merchant_id or "m_001")
    new_policy = await update_policy(target_merchant_id, data, session)
    return MerchantPolicySchema.model_validate(new_policy)
