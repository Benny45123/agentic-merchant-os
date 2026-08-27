from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base, TimestampMixin, generate_uuid
from app.core.enums import DecisionType

if TYPE_CHECKING:
    from app.models.intent import TransactionIntent
    from app.models.mandate import Mandate
    from app.models.order import Order
    from app.models.receipt import Receipt


class GuardianDecision(Base, TimestampMixin):
    __tablename__ = "guardian_decisions"

    decision_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    intent_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("transaction_intents.intent_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    campaign_proposal_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
        index=True
    )
    decision: Mapped[DecisionType] = mapped_column(
        SAEnum(DecisionType),
        nullable=False,
        index=True
    )
    # Ordered list of {name, passed, detail}
    checks: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    primary_reason: Mapped[str] = mapped_column(String(500), nullable=False)
    final_verified_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mandate_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("mandates.mandate_id", ondelete="SET NULL"),
        nullable=True
    )
    policy_version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    intent: Mapped[Optional["TransactionIntent"]] = relationship("TransactionIntent", back_populates="decision")
    mandate: Mapped[Optional["Mandate"]] = relationship("Mandate", back_populates="decisions")
    order: Mapped[Optional["Order"]] = relationship("Order", back_populates="decision", uselist=False)
    receipt: Mapped[Optional["Receipt"]] = relationship("Receipt", back_populates="guardian_decision", uselist=False)
