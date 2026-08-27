from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base, UpdatedTimestampMixin

if TYPE_CHECKING:
    from app.models.merchant import Merchant
    from app.models.catalog_snapshot import CatalogSnapshot
    from app.models.offer import Offer


class Product(Base, UpdatedTimestampMixin):
    __tablename__ = "products"

    sku: Mapped[str] = mapped_column(String(100), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("merchants.merchant_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Trusted & Authoritative Monetary / Inventory fields (stored as integers in smallest currency unit / paise)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    cost: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    inventory: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # UNTRUSTED Free-Text Field (Never used as authorization by Guardian)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    
    # Structured JSON Fields
    variants: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    shipping_info: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    return_policy: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    bundle_relationships: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    
    # Versioning & Security Flag
    catalog_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    suspicious_content_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="products")
    snapshots: Mapped[List["CatalogSnapshot"]] = relationship("CatalogSnapshot", back_populates="product", cascade="all, delete-orphan")
    offers: Mapped[List["Offer"]] = relationship("Offer", back_populates="product", cascade="all, delete-orphan")
