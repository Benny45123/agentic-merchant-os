from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.buyer import Buyer
    from app.models.decision import GuardianDecision


class Mandate(Base, TimestampMixin):
    __tablename__ = "mandates"

    mandate_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    buyer_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("buyers.buyer_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    max_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    max_quantity_per_item: Mapped[int] = mapped_column(Integer, nullable=False)
    allowed_categories: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    allowed_merchants: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    allowed_products: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    confirmation_required_above: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    signature: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Headless Razorpay UPI AutoPay Fields
    autopay_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    autopay_token: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    customer_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    max_amount_per_charge: Mapped[int] = mapped_column(Integer, default=10000000, nullable=False)
    recurring_auth_status: Mapped[str] = mapped_column(String(32), default="NONE", nullable=False)
    autopay_bank_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    autopay_vpa: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Relationships
    buyer: Mapped["Buyer"] = relationship("Buyer", back_populates="mandates")

    decisions: Mapped[List["GuardianDecision"]] = relationship("GuardianDecision", back_populates="mandate")
