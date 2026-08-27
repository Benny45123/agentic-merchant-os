from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.campaign.schemas import (
    CampaignActivateResponse,
    CampaignProposal,
    CampaignProposeRequest,
    CampaignStatusResponse,
)
from app.campaign.service import (
    activate_campaign,
    get_campaign_status,
    propose_campaign,
)
from app.core.auth import CurrentUser, get_current_user, get_optional_user
from app.core.db import get_session

router = APIRouter(prefix="/campaign", tags=["Campaign Orchestrator"])


@router.post("/propose", response_model=CampaignProposal)
async def propose_new_campaign(
    body: CampaignProposeRequest,
    session: AsyncSession = Depends(get_session),
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
):
    """
    Merchant states revenue objective in natural language.
    LLM proposes a bounded campaign and Guardian validates it deterministically.
    """
    try:
        return await propose_campaign(
            merchant_id=body.merchant_id,
            objective=body.objective,
            session=session,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{proposal_id}/activate", response_model=CampaignActivateResponse)
async def activate_approved_campaign(
    proposal_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
):
    """
    Activates an approved or confirmed campaign proposal.
    Writes bounded static Offer rows to the catalog.
    """
    try:
        campaign = await activate_campaign(proposal_id, session)
        return CampaignActivateResponse(
            campaign_id=campaign.campaign_id,
            status=campaign.status.value if hasattr(campaign.status, "value") else str(campaign.status),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{campaign_id}/status", response_model=CampaignStatusResponse)
async def get_status(
    campaign_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
):
    """Retrieve live campaign status and attributed revenue metrics."""
    try:
        return await get_campaign_status(campaign_id, session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
