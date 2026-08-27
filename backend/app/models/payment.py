from typing import Any, Dict, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.order import Order


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    payment_id: Mapped[str] = mapped_column(String(100), primary_key=True)  # Razorpay payment id
    order_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("orders.order_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    raw_webhook_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="payments")
