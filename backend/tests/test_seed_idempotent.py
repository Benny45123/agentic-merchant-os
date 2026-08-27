import pytest
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.seed import seed_data, DEMO_MERCHANT_ID, DEMO_BUYER_ID
from app.models import Merchant, Buyer, Product, Mandate, MerchantPolicy, CampaignPolicy, Offer, CatalogSnapshot


@pytest.mark.asyncio
async def test_seed_idempotent(test_db_session: AsyncSession):
    """Verifies that running seed_data once or multiple times succeeds idempotently without duplicate rows."""
    
    # First seed run
    await seed_data(test_db_session)
    
    # Count rows after first run
    res_m = await test_db_session.scalar(select(func.count(Merchant.merchant_id)))
    res_b = await test_db_session.scalar(select(func.count(Buyer.buyer_id)))
    res_p = await test_db_session.scalar(select(func.count(Product.sku)))
    res_mand = await test_db_session.scalar(select(func.count(Mandate.mandate_id)))
    res_pol = await test_db_session.scalar(select(func.count(MerchantPolicy.policy_id)))
    res_cpol = await test_db_session.scalar(select(func.count(CampaignPolicy.merchant_id)))
    
    assert res_m == 1
    assert res_b == 1
    assert res_p >= 8
    assert res_mand == 1
    assert res_pol == 1
    assert res_cpol == 1
    
    # Verify malicious fixture product exists
    attack_product = await test_db_session.get(Product, "ATTACK-SKU-001")
    assert attack_product is not None
    assert attack_product.suspicious_content_flag is True
    assert "SYSTEM OVERRIDE" in attack_product.description
    
    # Verify bundle trio exists
    hp = await test_db_session.get(Product, "HP-001")
    wrnty = await test_db_session.get(Product, "WRNTY-1Y")
    case = await test_db_session.get(Product, "CASE-HP")
    assert hp is not None
    assert wrnty is not None
    assert case is not None
    
    # Second seed run (Idempotency check)
    await seed_data(test_db_session)
    
    # Verify counts remain identical
    res_m2 = await test_db_session.scalar(select(func.count(Merchant.merchant_id)))
    res_b2 = await test_db_session.scalar(select(func.count(Buyer.buyer_id)))
    res_p2 = await test_db_session.scalar(select(func.count(Product.sku)))
    res_mand2 = await test_db_session.scalar(select(func.count(Mandate.mandate_id)))
    res_pol2 = await test_db_session.scalar(select(func.count(MerchantPolicy.policy_id)))
    res_cpol2 = await test_db_session.scalar(select(func.count(CampaignPolicy.merchant_id)))
    
    assert res_m2 == res_m
    assert res_b2 == res_b
    assert res_p2 == res_p
    assert res_mand2 == res_mand
    assert res_pol2 == res_pol
    assert res_cpol2 == res_cpol
