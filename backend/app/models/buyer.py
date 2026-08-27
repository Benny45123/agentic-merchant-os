from typing import List, TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.mandate import Mandate
    from app.models.intent import TransactionIntent
    from app.models.order import Order


class Buyer(Base, TimestampMixin):
    __tablename__ = "buyers"

    buyer_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    mandates: Mapped[List["Mandate"]] = relationship("Mandate", back_populates="buyer", cascade="all, delete-orphan")
    intents: Mapped[List["TransactionIntent"]] = relationship("TransactionIntent", back_populates="buyer")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="buyer")
