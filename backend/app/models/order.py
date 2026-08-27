from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base, TimestampMixin
from app.core.enums import OrderStatus

if TYPE_CHECKING:
    from app.models.merchant import Merchant
    from app.models.buyer import Buyer
    from app.models.decision import GuardianDecision
    from app.models.campaign import Campaign
    from app.models.payment import Payment


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(String(100), primary_key=True)  # Razorpay order id
    decision_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("guardian_decisions.decision_id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    merchant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("merchants.merchant_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    buyer_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("buyers.buyer_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus),
        default=OrderStatus.CREATED,
        nullable=False,
        index=True
    )
    campaign_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("campaigns.campaign_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="orders")
    buyer: Mapped["Buyer"] = relationship("Buyer", back_populates="orders")
    decision: Mapped["GuardianDecision"] = relationship("GuardianDecision", back_populates="order")
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign", back_populates="orders")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
