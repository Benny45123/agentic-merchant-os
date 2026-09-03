"""
Persistent Omnichannel Identity Resolution & Auto-Provisioning Engine.
Provides zero-friction, persistent identity resolution across Web, Telegram, and Claude MCP.
"""

from datetime import timedelta
import logging
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import generate_uuid, utc_now
from app.models.buyer import Buyer
from app.models.mandate import Mandate
from app.mandate.ap2_service import get_or_create_buyer_keypair

logger = logging.getLogger("identity_service")


async def ensure_buyer_and_mandate(
    session: AsyncSession,
    buyer_id: str,
    display_name: Optional[str] = None,
    channel: str = "web",
    initial_pool_paise: int = 5000000,  # ₹50,000.00 baseline
) -> Tuple[Buyer, Mandate]:
    """
    Ensures a buyer exists in the database with an active AutoPay spending pool
    and pre-computed Google AP2 ES256 keypair.
    Idempotent: If buyer & mandate already exist, loads and returns them without modification.
    """
    clean_id = (buyer_id or "").strip()
    if not clean_id:
        clean_id = f"b_dev_{generate_uuid()[:8]}"

    # 1. Resolve or Create Buyer
    stmt_buyer = select(Buyer).where(Buyer.buyer_id == clean_id)
    res_buyer = await session.execute(stmt_buyer)
    buyer = res_buyer.scalar_one_or_none()

    if not buyer:
        if not display_name:
            if clean_id.startswith("tg_"):
                display_name = f"Telegram Shopper ({clean_id[3:]})"
            elif clean_id.startswith("claude_"):
                display_name = f"Claude Desktop ({clean_id[7:]})"
            elif clean_id.startswith("b_dev_"):
                display_name = f"Web Shopper ({clean_id[6:]})"
            else:
                display_name = f"Shopper ({clean_id})"

        buyer = Buyer(
            buyer_id=clean_id,
            name=display_name,
            created_at=utc_now(),
        )
        session.add(buyer)
        await session.flush()
        logger.info(f"Auto-provisioned new buyer: {clean_id} ('{display_name}')")

    # 2. Resolve or Create Mandate
    stmt_mandate = select(Mandate).where(Mandate.buyer_id == clean_id, Mandate.active == True)
    res_mandate = await session.execute(stmt_mandate)
    mandate = res_mandate.scalar_one_or_none()

    pool_cap = max(20000000, initial_pool_paise)  # Baseline ₹2,00,000 to accommodate laptops (e.g. ₹89,990)

    if mandate:
        if mandate.autopay_token == f"tok_rzp_autopay_{clean_id}":
            # Reset pre-authorized placeholder token: AutoPay must only be enabled
            # when the user explicitly activates it via Claude or Telegram
            mandate.autopay_enabled = False
            mandate.autopay_token = None
            mandate.recurring_auth_status = "INACTIVE"

        # Upgrade outdated mandate caps (e.g. old ₹10,000 defaults) to the ₹2,00,000 baseline
        if (mandate.max_amount or 0) < pool_cap:
            mandate.max_amount = pool_cap
            mandate.max_amount_per_charge = pool_cap
            mandate.confirmation_required_above = pool_cap

        await session.flush()

    if not mandate:
        # Create active shopping mandate (AutoPay is OFF until user explicitly opts in)
        vpa_domain = "okhdfcbank"
        bank_name = "HDFC Bank (UPI AutoPay)"
        if "icici" in clean_id.lower():
            vpa_domain = "okicicibank"
            bank_name = "ICICI Bank (UPI AutoPay)"
        elif "sbi" in clean_id.lower():
            vpa_domain = "oksbi"
            bank_name = "State Bank of India (UPI AutoPay)"

        clean_vpa = f"{clean_id}@{vpa_domain}".replace("-", "_")

        mandate = Mandate(
            mandate_id=generate_uuid(),
            buyer_id=clean_id,
            max_amount=pool_cap,
            max_quantity_per_item=10,
            allowed_categories=["audio", "accessories", "wearables", "mobiles", "laptops", "electronics"],
            allowed_merchants=["m_001"],
            currency="INR",
            expires_at=utc_now() + timedelta(days=365),
            confirmation_required_above=pool_cap,
            signature=f"sig_mandate_{clean_id}",
            active=True,
            spent_amount=0,
            autopay_enabled=False,  # AutoPay is OFF by default until explicitly enabled by the user!
            autopay_token=None,
            customer_id=f"cust_{clean_id}",
            max_amount_per_charge=pool_cap,
            recurring_auth_status="INACTIVE",
            autopay_bank_name=bank_name,
            autopay_vpa=clean_vpa,
            created_at=utc_now(),
        )
        session.add(mandate)
        await session.flush()
        logger.info(f"Auto-provisioned ₹{pool_cap/100:.2f} baseline mandate for {clean_id} (AutoPay: OFF)")

    # 3. Ensure Google AP2 ES256 Keypair is available
    get_or_create_buyer_keypair(clean_id)

    return buyer, mandate
