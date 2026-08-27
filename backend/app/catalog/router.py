from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.schemas import (
    OfferSummarySchema,
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.catalog.service import (
    create_product,
    get_product,
    search_products,
    update_product,
)
from app.core.auth import CurrentUser, get_current_user, get_optional_user
from app.core.db import get_session
from app.models import Product

router = APIRouter(prefix="/catalog", tags=["Catalog"])


def map_product_to_response(product: Product) -> ProductResponse:
    offers_summary = [
        OfferSummarySchema(
            offer_id=offer.offer_id,
            type=offer.type.value if hasattr(offer.type, "value") else str(offer.type),
            label=offer.label,
            discount_pct=offer.discount_pct,
            expires_at=offer.ends_at,
        )
        for offer in (product.offers or [])
    ]

    return ProductResponse(
        sku=product.sku,
        name=product.name,
        category=product.category,
        price=product.price,
        currency=product.currency,
        inventory=product.inventory,
        description=product.description,
        variants=product.variants or [],
        shipping_info=product.shipping_info or {},
        return_policy=product.return_policy or {},
        offers=offers_summary,
        bundle_relationships=product.bundle_relationships or [],
        catalog_version=product.catalog_version,
        suspicious_content_flag=product.suspicious_content_flag,
    )


@router.get("/products", response_model=ProductListResponse)
async def list_products(
    merchant_id: str = Query(..., description="Target merchant UUID"),
    q: Optional[str] = Query(None, description="Free text search query"),
    category: Optional[str] = Query(None, description="Category filter"),
    session: AsyncSession = Depends(get_session),
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
):
    """List and search merchant catalog products."""
    products = await search_products(
        merchant_id=merchant_id,
        query=q,
        category=category,
        session=session,
    )
    return ProductListResponse(products=[map_product_to_response(p) for p in products])


@router.get("/products/{sku}", response_model=ProductResponse)
async def get_product_by_sku(
    sku: str,
    session: AsyncSession = Depends(get_session),
    current_user: Optional[CurrentUser] = Depends(get_optional_user),
):
    """Retrieve details for a single SKU."""
    product = await get_product(sku, session)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU '{sku}' not found"
        )
    return map_product_to_response(product)


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_new_product(
    data: ProductCreate,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Create a new catalog product (Merchant only)."""
    if not current_user.is_merchant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only merchants can create products"
        )

    # Check if SKU already exists
    existing = await get_product(data.sku, session)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with SKU '{data.sku}' already exists"
        )

    product = await create_product(
        merchant_id=current_user.sub,
        data=data,
        session=session
    )
    return map_product_to_response(product)


@router.patch("/products/{sku}", response_model=ProductResponse)
async def patch_product(
    sku: str,
    data: ProductUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Update product fields. Price/inventory updates increment catalog_version."""
    if not current_user.is_merchant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only merchants can update products"
        )

    try:
        updated_product = await update_product(sku, data, session)
        return map_product_to_response(updated_product)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
