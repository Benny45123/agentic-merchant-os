from typing import List, Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.catalog.schemas import AuthoritativeState, ProductCreate, ProductUpdate
from app.core.base import generate_uuid, utc_now
from app.models import CatalogSnapshot, Offer, Product


async def get_product(sku: str, session: AsyncSession) -> Optional[Product]:
    """Retrieve a single product by SKU with its active offers."""
    query = (
        select(Product)
        .where(Product.sku == sku)
        .options(selectinload(Product.offers))
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def search_products(
    merchant_id: str,
    query: Optional[str] = None,
    category: Optional[str] = None,
    session: AsyncSession = None,
) -> List[Product]:
    """Search products for a merchant with optional text and category filters."""
    stmt = (
        select(Product)
        .where(Product.merchant_id == merchant_id)
        .options(selectinload(Product.offers))
    )

    if category:
        stmt = stmt.where(Product.category.ilike(category))

    # If query is empty, wildcard, or request for all/full catalog, return everything without filtering
    clean_q = query.strip() if query else ""
    if clean_q and clean_q.lower() not in ("*", "all", "full", "everything", "all products", "catalog", "full catalog"):
        terms = [t for t in clean_q.split() if len(t) >= 2]
        if terms:
            # 1. Try strict matching: all terms must match
            and_clauses = []
            for t in terms:
                term_str = f"%{t}%"
                and_clauses.append(
                    or_(
                        Product.name.ilike(term_str),
                        Product.sku.ilike(term_str),
                        Product.category.ilike(term_str),
                        Product.description.ilike(term_str),
                    )
                )
            strict_res = await session.execute(stmt.where(*and_clauses))
            strict_results = list(strict_res.scalars().all())
            if strict_results:
                return strict_results

            # 2. Fallback: match ANY term (e.g. "headphones case audio" matches items containing any of those words)
            or_clauses = []
            for t in terms:
                term_str = f"%{t}%"
                or_clauses.append(
                    or_(
                        Product.name.ilike(term_str),
                        Product.sku.ilike(term_str),
                        Product.category.ilike(term_str),
                        Product.description.ilike(term_str),
                    )
                )
            stmt = stmt.where(or_(*or_clauses))
        else:
            search_term = f"%{clean_q}%"
            stmt = stmt.where(
                or_(
                    Product.name.ilike(search_term),
                    Product.sku.ilike(search_term),
                    Product.category.ilike(search_term),
                    Product.description.ilike(search_term),
                )
            )

    result = await session.execute(stmt)
    return list(result.scalars().all())



async def get_authoritative_state(sku: str, session: AsyncSession) -> AuthoritativeState:
    """
    Guardian-only consumer.
    Must always query the database directly to ensure zero caching/stale reads.
    """
    stmt = select(Product).where(Product.sku == sku)
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        return AuthoritativeState(
            sku=sku,
            price=0,
            cost=None,
            inventory=0,
            currency="INR",
            category="",
            merchant_id="",
            catalog_version=0,
            exists=False,
            suspicious_content_flag=False,
        )

    return AuthoritativeState(
        sku=product.sku,
        price=product.price,
        cost=product.cost,
        inventory=product.inventory,
        currency=product.currency,
        category=product.category,
        merchant_id=product.merchant_id,
        catalog_version=product.catalog_version,
        exists=True,
        suspicious_content_flag=product.suspicious_content_flag,
    )


async def snapshot_catalog(sku: str, session: AsyncSession) -> CatalogSnapshot:
    """
    Captures an immutable snapshot of a product's current catalog state.
    Called when an item is added to the cart by the Commerce Agent.
    """
    product = await get_product(sku, session)
    if not product:
        raise ValueError(f"Product with SKU '{sku}' does not exist")

    snapshot = CatalogSnapshot(
        snapshot_id=generate_uuid(),
        sku=product.sku,
        catalog_version=product.catalog_version,
        price=product.price,
        inventory=product.inventory,
        captured_at=utc_now(),
    )
    session.add(snapshot)
    await session.flush()
    return snapshot


async def create_product(
    merchant_id: str,
    data: ProductCreate,
    session: AsyncSession
) -> Product:
    """Create a new product row."""
    product = Product(
        sku=data.sku,
        merchant_id=merchant_id,
        name=data.name,
        category=data.category,
        price=data.price,
        cost=data.cost,
        currency=data.currency,
        inventory=data.inventory,
        description=data.description,
        variants=[v.model_dump() for v in data.variants],
        shipping_info=data.shipping_info,
        return_policy=data.return_policy,
        bundle_relationships=[b.model_dump() for b in data.bundle_relationships],
        catalog_version=1,
        suspicious_content_flag=False,
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    session.add(product)
    await session.flush()
    return product


async def update_product(
    sku: str,
    data: ProductUpdate,
    session: AsyncSession
) -> Product:
    """
    Update product fields.
    Price and inventory changes ALWAYS increment catalog_version atomically.
    """
    product = await get_product(sku, session)
    if not product:
        raise ValueError(f"Product with SKU '{sku}' not found")

    version_increment_needed = False

    if data.name is not None:
        product.name = data.name
    if data.category is not None:
        product.category = data.category
    if data.description is not None:
        product.description = data.description
    if data.cost is not None:
        product.cost = data.cost
    if data.shipping_info is not None:
        product.shipping_info = data.shipping_info
    if data.return_policy is not None:
        product.return_policy = data.return_policy
    if data.variants is not None:
        product.variants = [v.model_dump() for v in data.variants]
    if data.bundle_relationships is not None:
        product.bundle_relationships = [b.model_dump() for b in data.bundle_relationships]
    if data.suspicious_content_flag is not None:
        product.suspicious_content_flag = data.suspicious_content_flag

    # Check for price or inventory modification
    if data.price is not None and data.price != product.price:
        product.price = data.price
        version_increment_needed = True

    if data.inventory is not None and data.inventory != product.inventory:
        product.inventory = data.inventory
        version_increment_needed = True

    if version_increment_needed:
        product.catalog_version += 1

    product.updated_at = utc_now()
    await session.flush()
    return product
