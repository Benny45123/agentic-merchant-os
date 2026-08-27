from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.merchant import Merchant


class MerchantPolicy(Base, TimestampMixin):
    __tablename__ = "merchant_policies"

    policy_id: Mapped[str] = mapped_column(
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
    maximum_discount_pct: Mapped[int] = mapped_column(Integer, nullable=False)
    minimum_margin_pct: Mapped[int] = mapped_column(Integer, nullable=False)
    maximum_order_value: Mapped[int] = mapped_column(Integer, nullable=False)
    allowed_products_for_discount: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    minimum_stock_to_sell: Mapped[int] = mapped_column(Integer, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False, index=True)

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="policies")


class CampaignPolicy(Base, TimestampMixin):
    __tablename__ = "campaign_policies"

    merchant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("merchants.merchant_id", ondelete="CASCADE"),
        primary_key=True
    )
    allowed_campaign_discount_pct: Mapped[int] = mapped_column(Integer, nullable=False)
    campaign_budget_default: Mapped[int] = mapped_column(Integer, nullable=False)
    daily_campaign_budget_cap: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="campaign_policies")
