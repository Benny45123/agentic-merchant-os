from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base, TimestampMixin, generate_uuid
from app.core.enums import OfferType

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.campaign import Campaign


class Offer(Base, TimestampMixin):
    __tablename__ = "offers"

    offer_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    sku: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("products.sku", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    type: Mapped[OfferType] = mapped_column(
        SAEnum(OfferType),
        nullable=False,
        default=OfferType.MERCHANT_DEFINED
    )
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    discount_pct: Mapped[int] = mapped_column(Integer, nullable=False)
    campaign_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("campaigns.campaign_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    starts_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="offers")
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign", back_populates="offers")
