import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.schemas import ProductCreate, ProductUpdate
from app.catalog.service import (
    create_product,
    get_authoritative_state,
    get_product,
    search_products,
    snapshot_catalog,
    update_product,
)
from app.seed import DEMO_MERCHANT_ID, seed_data


@pytest.mark.asyncio
async def test_catalog_crud_and_version_increment(test_db_session: AsyncSession):
    await seed_data(test_db_session)

    # 1. Search products
    products = await search_products(
        merchant_id=DEMO_MERCHANT_ID,
        query="headphones",
        category=None,
        session=test_db_session,
    )
    assert len(products) >= 1
    assert any(p.sku == "HP-001" for p in products)

    # 2. Get Authoritative state
    auth_state = await get_authoritative_state("HP-001", test_db_session)
    assert auth_state.exists is True
    assert auth_state.price == 449900
    assert auth_state.inventory == 42
    assert auth_state.catalog_version == 17

    # 3. Snapshot catalog
    snap = await snapshot_catalog("HP-001", test_db_session)
    assert snap.sku == "HP-001"
    assert snap.catalog_version == 17
    assert snap.price == 449900

    # 4. Update description only -> catalog_version MUST NOT change
    p_updated = await update_product(
        "HP-001",
        ProductUpdate(description="Updated description only"),
        test_db_session,
    )
    assert p_updated.catalog_version == 17

    # 5. Update price -> catalog_version MUST increment
    p_updated2 = await update_product(
        "HP-001",
        ProductUpdate(price=469900),
        test_db_session,
    )
    assert p_updated2.catalog_version == 18
    assert p_updated2.price == 469900

    # 6. Authoritative state reflects new price immediately
    auth_state2 = await get_authoritative_state("HP-001", test_db_session)
    assert auth_state2.price == 469900
    assert auth_state2.catalog_version == 18
