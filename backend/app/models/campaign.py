from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base, TimestampMixin, generate_uuid
from app.core.enums import CampaignEventType, CampaignStatus

if TYPE_CHECKING:
    from app.models.merchant import Merchant
    from app.models.offer import Offer
    from app.models.decision import GuardianDecision
    from app.models.order import Order


class Campaign(Base, TimestampMixin):
    __tablename__ = "campaigns"

    campaign_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    merchant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("merchants.merchant_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    objective_text: Mapped[str] = mapped_column(Text, nullable=False)
    eligible_skus: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    discount_pct: Mapped[int] = mapped_column(Integer, nullable=False)
    bundle_offer: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    budget: Mapped[int] = mapped_column(Integer, nullable=False)
    budget_spent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[CampaignStatus] = mapped_column(
        SAEnum(CampaignStatus),
        default=CampaignStatus.DRAFT,
        nullable=False,
        index=True
    )
    pause_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    guardian_decision_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("guardian_decisions.decision_id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="campaigns")
    offers: Mapped[List["Offer"]] = relationship("Offer", back_populates="campaign")
    events: Mapped[List["CampaignEvent"]] = relationship("CampaignEvent", back_populates="campaign", cascade="all, delete-orphan")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="campaign")
    guardian_decision: Mapped[Optional["GuardianDecision"]] = relationship("GuardianDecision", foreign_keys=[guardian_decision_id])


class CampaignEvent(Base, TimestampMixin):
    __tablename__ = "campaign_events"

    event_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    campaign_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("campaigns.campaign_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    type: Mapped[CampaignEventType] = mapped_column(
        SAEnum(CampaignEventType),
        nullable=False,
        index=True
    )
    detail: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="events")
