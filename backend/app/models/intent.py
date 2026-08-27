from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.buyer import Buyer
    from app.models.merchant import Merchant
    from app.models.decision import GuardianDecision


class TransactionIntent(Base, TimestampMixin):
    __tablename__ = "transaction_intents"

    intent_id: Mapped[str] = mapped_column(
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
    merchant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("merchants.merchant_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    # Items: list of {sku, variant_id, qty, observed_price, catalog_version, snapshot_id}
    items: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    requested_discount_pct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    buyer: Mapped["Buyer"] = relationship("Buyer", back_populates="intents")
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="intents")
    decision: Mapped[Optional["GuardianDecision"]] = relationship("GuardianDecision", back_populates="intent", uselist=False)
