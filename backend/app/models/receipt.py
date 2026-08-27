from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base, TimestampMixin, generate_uuid
from app.core.enums import DecisionType

if TYPE_CHECKING:
    from app.models.merchant import Merchant
    from app.models.decision import GuardianDecision


class Receipt(Base, TimestampMixin):
    __tablename__ = "receipts"

    receipt_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    decision_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("guardian_decisions.decision_id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    intent_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    buyer_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    merchant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("merchants.merchant_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Frozen Snapshots for Audit Integrity (denormalized on purpose per spec)
    items_snapshot: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    catalog_snapshot_ids: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    observed_total: Mapped[int] = mapped_column(Integer, nullable=False)
    final_verified_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mandate_snapshot: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    policy_snapshot: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    guardian_checks: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    
    # Decision Outcome
    decision: Mapped[DecisionType] = mapped_column(
        SAEnum(DecisionType),
        nullable=False,
        index=True
    )
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Payment State Mirrors
    razorpay_order_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    razorpay_payment_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="receipts")
    guardian_decision: Mapped["GuardianDecision"] = relationship("GuardianDecision", back_populates="receipt")
