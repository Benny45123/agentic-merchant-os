from enum import Enum


class DecisionType(str, Enum):
    APPROVE = "APPROVE"
    BLOCK = "BLOCK"
    REQUIRE_CONFIRMATION = "REQUIRE_CONFIRMATION"


class CampaignStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"


class CampaignEventType(str, Enum):
    ACTIVATED = "ACTIVATED"
    ORDER_ATTRIBUTED = "ORDER_ATTRIBUTED"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"


class OrderStatus(str, Enum):
    CREATED = "CREATED"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class OfferType(str, Enum):
    MERCHANT_DEFINED = "merchant_defined"
    CAMPAIGN_DISCOUNT = "campaign_discount"


class UserRole(str, Enum):
    BUYER = "buyer"
    MERCHANT = "merchant"
