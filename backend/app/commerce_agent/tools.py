from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.service import get_product, search_products, snapshot_catalog
from app.commerce_agent.schemas import CartItemSchema, CartSchema
from app.mandate.service import get_active_mandate


class CommerceAgentTools:
    def __init__(
        self,
        session_id: str,
        buyer_id: str,
        merchant_id: str,
        cart: CartSchema,
        session: AsyncSession,
    ):
        self.session_id = session_id
        self.buyer_id = buyer_id
        self.merchant_id = merchant_id
        self.cart = cart
        self.session = session

    async def search_catalog(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search merchant catalog products."""
        products = await search_products(
            merchant_id=self.merchant_id,
            query=query,
            category=category,
            session=self.session,
        )
        return [
            {
                "sku": p.sku,
                "name": p.name,
                "category": p.category,
                "price": p.price,
                "inventory": p.inventory,
                "description": p.description,
                "variants": p.variants,
                "bundle_relationships": p.bundle_relationships,
            }
            for p in products
        ]

    async def get_product_details(self, sku: str) -> Optional[Dict[str, Any]]:
        """Get product details by SKU."""
        product = await get_product(sku, self.session)
        if not product:
            return None
        return {
            "sku": product.sku,
            "name": product.name,
            "category": product.category,
            "price": product.price,
            "inventory": product.inventory,
            "description": product.description,
            "variants": product.variants,
            "bundle_relationships": product.bundle_relationships,
        }

    async def add_to_cart(
        self,
        sku: str,
        qty: int = 1,
        variant_id: Optional[str] = None,
        source: str = "organic",
    ) -> Dict[str, Any]:
        """
        Adds item to session cart after taking a fresh CatalogSnapshot.
        Enforces mandate quantity limits with explainable error (never silent clamp).
        """
        product = await get_product(sku, self.session)
        if not product:
            return {"success": False, "error": f"Product with SKU '{sku}' not found in catalog"}

        if product.inventory < qty:
            return {
                "success": False,
                "error": f"Insufficient stock: requested {qty} units, but only {product.inventory} available",
            }

        # Check Mandate limits
        mandate = await get_active_mandate(self.buyer_id, self.session)
        if mandate and qty > mandate.max_quantity_per_item:
            return {
                "success": False,
                "error": f"Requested quantity ({qty}) exceeds your buyer mandate limit of {mandate.max_quantity_per_item} units per item",
            }

        # Create immutable CatalogSnapshot
        snapshot = await snapshot_catalog(sku, self.session)

        # Check if already in cart
        existing_item = next((item for item in self.cart.items if item.sku == sku), None)
        if existing_item:
            new_qty = existing_item.qty + qty
            if mandate and new_qty > mandate.max_quantity_per_item:
                return {
                    "success": False,
                    "error": f"Combined quantity ({new_qty}) in cart would exceed buyer mandate limit of {mandate.max_quantity_per_item} units",
                }
            existing_item.qty = new_qty
            existing_item.observed_price = product.price
            existing_item.catalog_version = product.catalog_version
            existing_item.snapshot_id = snapshot.snapshot_id
        else:
            self.cart.items.append(
                CartItemSchema(
                    sku=product.sku,
                    variant_id=variant_id,
                    qty=qty,
                    observed_price=product.price,
                    catalog_version=product.catalog_version,
                    snapshot_id=snapshot.snapshot_id,
                    source=source,
                )
            )

        self.cart.subtotal = sum(i.observed_price * i.qty for i in self.cart.items)
        return {
            "success": True,
            "sku": product.sku,
            "name": product.name,
            "qty": qty,
            "subtotal": self.cart.subtotal,
        }

    async def remove_from_cart(self, sku: str) -> Dict[str, Any]:
        """Removes item from cart."""
        self.cart.items = [i for i in self.cart.items if i.sku != sku]
        self.cart.subtotal = sum(i.observed_price * i.qty for i in self.cart.items)
        return {"success": True, "subtotal": self.cart.subtotal}

    def get_cart(self) -> CartSchema:
        """Read current cart."""
        self.cart.subtotal = sum(i.observed_price * i.qty for i in self.cart.items)
        return self.cart
