from typing import List, TYPE_CHECKING
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.policy import MerchantPolicy, CampaignPolicy
    from app.models.campaign import Campaign
    from app.models.intent import TransactionIntent
    from app.models.order import Order
    from app.models.receipt import Receipt


class Merchant(Base, TimestampMixin):
    __tablename__ = "merchants"

    merchant_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    razorpay_key_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="merchant", cascade="all, delete-orphan")
    policies: Mapped[List["MerchantPolicy"]] = relationship("MerchantPolicy", back_populates="merchant", cascade="all, delete-orphan")
    campaign_policies: Mapped[List["CampaignPolicy"]] = relationship("CampaignPolicy", back_populates="merchant", cascade="all, delete-orphan")
    campaigns: Mapped[List["Campaign"]] = relationship("Campaign", back_populates="merchant", cascade="all, delete-orphan")
    intents: Mapped[List["TransactionIntent"]] = relationship("TransactionIntent", back_populates="merchant")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="merchant")
    receipts: Mapped[List["Receipt"]] = relationship("Receipt", back_populates="merchant")
