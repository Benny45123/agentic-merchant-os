from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class VariantSchema(BaseModel):
    variant_id: str
    label: str
    price_delta: int = 0
    inventory: int = 0


class ShippingInfoSchema(BaseModel):
    eta_days: int = 3
    free_above: int = 0


class ReturnPolicySchema(BaseModel):
    window_days: int = 7
    conditions: str = "Standard return policy"


class OfferSummarySchema(BaseModel):
    offer_id: str
    type: str
    label: str
    discount_pct: int
    expires_at: Optional[datetime] = None


class BundleRelationshipSchema(BaseModel):
    related_sku: str
    relation: str


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sku: str
    name: str
    category: str
    price: int
    currency: str = "INR"
    inventory: int
    description: str  # UNTRUSTED - for display/conversation only
    variants: List[VariantSchema] = Field(default_factory=list)
    shipping_info: Dict[str, Any] = Field(default_factory=dict)
    return_policy: Dict[str, Any] = Field(default_factory=dict)
    offers: List[OfferSummarySchema] = Field(default_factory=list)
    bundle_relationships: List[BundleRelationshipSchema] = Field(default_factory=list)
    catalog_version: int
    suspicious_content_flag: bool = False


class ProductListResponse(BaseModel):
    products: List[ProductResponse]


class ProductCreate(BaseModel):
    sku: str
    name: str
    category: str
    price: int = Field(gt=0, description="Price in smallest currency unit / paise")
    cost: Optional[int] = Field(default=None, description="Cost for margin calculation")
    currency: str = "INR"
    inventory: int = Field(ge=0, description="Available stock quantity")
    description: str = ""
    variants: List[VariantSchema] = Field(default_factory=list)
    shipping_info: Dict[str, Any] = Field(default_factory=dict)
    return_policy: Dict[str, Any] = Field(default_factory=dict)
    bundle_relationships: List[BundleRelationshipSchema] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[int] = Field(default=None, gt=0)
    cost: Optional[int] = None
    inventory: Optional[int] = Field(default=None, ge=0)
    description: Optional[str] = None
    variants: Optional[List[VariantSchema]] = None
    shipping_info: Optional[Dict[str, Any]] = None
    return_policy: Optional[Dict[str, Any]] = None
    bundle_relationships: Optional[List[BundleRelationshipSchema]] = None
    suspicious_content_flag: Optional[bool] = None


class AuthoritativeState(BaseModel):
    sku: str
    price: int
    cost: Optional[int] = None
    inventory: int
    currency: str = "INR"
    category: str
    merchant_id: str
    catalog_version: int
    exists: bool = True
    suspicious_content_flag: bool = False
