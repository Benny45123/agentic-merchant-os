"""initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-27 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Merchants table
    op.create_table(
        "merchants",
        sa.Column("merchant_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("razorpay_key_id", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("merchant_id"),
    )

    # Buyers table
    op.create_table(
        "buyers",
        sa.Column("buyer_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("buyer_id"),
    )

    # Products table
    op.create_table(
        "products",
        sa.Column("sku", sa.String(length=100), nullable=False),
        sa.Column("merchant_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("cost", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("inventory", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("variants", sa.JSON(), nullable=False),
        sa.Column("shipping_info", sa.JSON(), nullable=False),
        sa.Column("return_policy", sa.JSON(), nullable=False),
        sa.Column("bundle_relationships", sa.JSON(), nullable=False),
        sa.Column("catalog_version", sa.Integer(), nullable=False),
        sa.Column("suspicious_content_flag", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.merchant_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("sku"),
    )
    op.create_index("ix_products_merchant_id", "products", ["merchant_id"])
    op.create_index("ix_products_category", "products", ["category"])

    # Catalog Snapshots table
    op.create_table(
        "catalog_snapshots",
        sa.Column("snapshot_id", sa.String(length=36), nullable=False),
        sa.Column("sku", sa.String(length=100), nullable=False),
        sa.Column("catalog_version", sa.Integer(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("inventory", sa.Integer(), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["sku"], ["products.sku"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("snapshot_id"),
    )
    op.create_index("ix_catalog_snapshots_sku", "catalog_snapshots", ["sku"])

    # Mandates table
    op.create_table(
        "mandates",
        sa.Column("mandate_id", sa.String(length=36), nullable=False),
        sa.Column("buyer_id", sa.String(length=36), nullable=False),
        sa.Column("max_amount", sa.Integer(), nullable=False),
        sa.Column("max_quantity_per_item", sa.Integer(), nullable=False),
        sa.Column("allowed_categories", sa.JSON(), nullable=True),
        sa.Column("allowed_merchants", sa.JSON(), nullable=True),
        sa.Column("allowed_products", sa.JSON(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("confirmation_required_above", sa.Integer(), nullable=True),
        sa.Column("signature", sa.String(length=512), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["buyer_id"], ["buyers.buyer_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("mandate_id"),
    )
    op.create_index("ix_mandates_buyer_id", "mandates", ["buyer_id"])
    op.create_index("ix_mandates_active", "mandates", ["active"])

    # Merchant Policies table
    op.create_table(
        "merchant_policies",
        sa.Column("policy_id", sa.String(length=36), nullable=False),
        sa.Column("merchant_id", sa.String(length=36), nullable=False),
        sa.Column("maximum_discount_pct", sa.Integer(), nullable=False),
        sa.Column("minimum_margin_pct", sa.Integer(), nullable=False),
        sa.Column("maximum_order_value", sa.Integer(), nullable=False),
        sa.Column("allowed_products_for_discount", sa.JSON(), nullable=True),
        sa.Column("minimum_stock_to_sell", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.merchant_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("policy_id"),
    )
    op.create_index("ix_merchant_policies_merchant_id", "merchant_policies", ["merchant_id"])
    op.create_index("ix_merchant_policies_version", "merchant_policies", ["version"])

    # Campaign Policies table
    op.create_table(
        "campaign_policies",
        sa.Column("merchant_id", sa.String(length=36), nullable=False),
        sa.Column("allowed_campaign_discount_pct", sa.Integer(), nullable=False),
        sa.Column("campaign_budget_default", sa.Integer(), nullable=False),
        sa.Column("daily_campaign_budget_cap", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.merchant_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("merchant_id"),
    )

    # Transaction Intents table
    op.create_table(
        "transaction_intents",
        sa.Column("intent_id", sa.String(length=36), nullable=False),
        sa.Column("buyer_id", sa.String(length=36), nullable=False),
        sa.Column("merchant_id", sa.String(length=36), nullable=False),
        sa.Column("items", sa.JSON(), nullable=False),
        sa.Column("requested_discount_pct", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["buyer_id"], ["buyers.buyer_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.merchant_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("intent_id"),
    )
    op.create_index("ix_transaction_intents_buyer_id", "transaction_intents", ["buyer_id"])
    op.create_index("ix_transaction_intents_merchant_id", "transaction_intents", ["merchant_id"])

    # Guardian Decisions table
    op.create_table(
        "guardian_decisions",
        sa.Column("decision_id", sa.String(length=36), nullable=False),
        sa.Column("intent_id", sa.String(length=36), nullable=True),
        sa.Column("campaign_proposal_id", sa.String(length=36), nullable=True),
        sa.Column(
            "decision",
            sa.Enum("APPROVE", "BLOCK", "REQUIRE_CONFIRMATION", name="decisiontype"),
            nullable=False
        ),
        sa.Column("checks", sa.JSON(), nullable=False),
        sa.Column("primary_reason", sa.String(length=500), nullable=False),
        sa.Column("final_verified_total", sa.Integer(), nullable=True),
        sa.Column("mandate_id", sa.String(length=36), nullable=True),
        sa.Column("policy_version", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["intent_id"], ["transaction_intents.intent_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["mandate_id"], ["mandates.mandate_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("decision_id"),
    )
    op.create_index("ix_guardian_decisions_intent_id", "guardian_decisions", ["intent_id"])
    op.create_index("ix_guardian_decisions_campaign_proposal_id", "guardian_decisions", ["campaign_proposal_id"])
    op.create_index("ix_guardian_decisions_decision", "guardian_decisions", ["decision"])

    # Campaigns table
    op.create_table(
        "campaigns",
        sa.Column("campaign_id", sa.String(length=36), nullable=False),
        sa.Column("merchant_id", sa.String(length=36), nullable=False),
        sa.Column("objective_text", sa.Text(), nullable=False),
        sa.Column("eligible_skus", sa.JSON(), nullable=False),
        sa.Column("discount_pct", sa.Integer(), nullable=False),
        sa.Column("bundle_offer", sa.JSON(), nullable=True),
        sa.Column("budget", sa.Integer(), nullable=False),
        sa.Column("budget_spent", sa.Integer(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum("DRAFT", "PENDING_APPROVAL", "ACTIVE", "PAUSED", "COMPLETED", name="campaignstatus"),
            nullable=False
        ),
        sa.Column("pause_reason", sa.String(length=255), nullable=True),
        sa.Column("guardian_decision_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.merchant_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["guardian_decision_id"], ["guardian_decisions.decision_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("campaign_id"),
    )
    op.create_index("ix_campaigns_merchant_id", "campaigns", ["merchant_id"])
    op.create_index("ix_campaigns_status", "campaigns", ["status"])

    # Offers table
    op.create_table(
        "offers",
        sa.Column("offer_id", sa.String(length=36), nullable=False),
        sa.Column("sku", sa.String(length=100), nullable=False),
        sa.Column(
            "type",
            sa.Enum("merchant_defined", "campaign_discount", name="offertype"),
            nullable=False
        ),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("discount_pct", sa.Integer(), nullable=False),
        sa.Column("campaign_id", sa.String(length=36), nullable=True),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["sku"], ["products.sku"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.campaign_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("offer_id"),
    )
    op.create_index("ix_offers_sku", "offers", ["sku"])
    op.create_index("ix_offers_campaign_id", "offers", ["campaign_id"])

    # Campaign Events table
    op.create_table(
        "campaign_events",
        sa.Column("event_id", sa.String(length=36), nullable=False),
        sa.Column("campaign_id", sa.String(length=36), nullable=False),
        sa.Column(
            "type",
            sa.Enum("ACTIVATED", "ORDER_ATTRIBUTED", "PAUSED", "COMPLETED", name="campaigneventtype"),
            nullable=False
        ),
        sa.Column("detail", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.campaign_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_index("ix_campaign_events_campaign_id", "campaign_events", ["campaign_id"])
    op.create_index("ix_campaign_events_type", "campaign_events", ["type"])

    # Orders table
    op.create_table(
        "orders",
        sa.Column("order_id", sa.String(length=100), nullable=False),
        sa.Column("decision_id", sa.String(length=36), nullable=False),
        sa.Column("merchant_id", sa.String(length=36), nullable=False),
        sa.Column("buyer_id", sa.String(length=36), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column(
            "status",
            sa.Enum("CREATED", "PAID", "FAILED", "REFUNDED", name="orderstatus"),
            nullable=False
        ),
        sa.Column("campaign_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["decision_id"], ["guardian_decisions.decision_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.merchant_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["buyer_id"], ["buyers.buyer_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.campaign_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("order_id"),
        sa.UniqueConstraint("decision_id"),
    )
    op.create_index("ix_orders_merchant_id", "orders", ["merchant_id"])
    op.create_index("ix_orders_buyer_id", "orders", ["buyer_id"])
    op.create_index("ix_orders_campaign_id", "orders", ["campaign_id"])
    op.create_index("ix_orders_status", "orders", ["status"])

    # Payments table
    op.create_table(
        "payments",
        sa.Column("payment_id", sa.String(length=100), nullable=False),
        sa.Column("order_id", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("verified", sa.Boolean(), nullable=False),
        sa.Column("raw_webhook_payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.order_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("payment_id"),
    )
    op.create_index("ix_payments_order_id", "payments", ["order_id"])

    # Receipts table
    op.create_table(
        "receipts",
        sa.Column("receipt_id", sa.String(length=36), nullable=False),
        sa.Column("decision_id", sa.String(length=36), nullable=False),
        sa.Column("intent_id", sa.String(length=36), nullable=True),
        sa.Column("buyer_id", sa.String(length=36), nullable=True),
        sa.Column("merchant_id", sa.String(length=36), nullable=False),
        sa.Column("items_snapshot", sa.JSON(), nullable=False),
        sa.Column("catalog_snapshot_ids", sa.JSON(), nullable=False),
        sa.Column("observed_total", sa.Integer(), nullable=False),
        sa.Column("final_verified_total", sa.Integer(), nullable=True),
        sa.Column("mandate_snapshot", sa.JSON(), nullable=True),
        sa.Column("policy_snapshot", sa.JSON(), nullable=True),
        sa.Column("guardian_checks", sa.JSON(), nullable=False),
        sa.Column(
            "decision",
            sa.Enum("APPROVE", "BLOCK", "REQUIRE_CONFIRMATION", name="decisiontype"),
            nullable=False
        ),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("razorpay_order_id", sa.String(length=100), nullable=True),
        sa.Column("razorpay_payment_id", sa.String(length=100), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["decision_id"], ["guardian_decisions.decision_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.merchant_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("receipt_id"),
        sa.UniqueConstraint("decision_id"),
    )
    op.create_index("ix_receipts_merchant_id", "receipts", ["merchant_id"])
    op.create_index("ix_receipts_buyer_id", "receipts", ["buyer_id"])
    op.create_index("ix_receipts_intent_id", "receipts", ["intent_id"])
    op.create_index("ix_receipts_decision", "receipts", ["decision"])
    op.create_index("ix_receipts_razorpay_order_id", "receipts", ["razorpay_order_id"])


def downgrade() -> None:
    op.drop_table("receipts")
    op.drop_table("payments")
    op.drop_table("orders")
    op.drop_table("campaign_events")
    op.drop_table("offers")
    op.drop_table("campaigns")
    op.drop_table("guardian_decisions")
    op.drop_table("transaction_intents")
    op.drop_table("campaign_policies")
    op.drop_table("merchant_policies")
    op.drop_table("mandates")
    op.drop_table("catalog_snapshots")
    op.drop_table("products")
    op.drop_table("buyers")
    op.drop_table("merchants")
