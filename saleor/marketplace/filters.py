"""Filter utilities for marketplace tenant isolation."""

from typing import TYPE_CHECKING, Optional

from django.db.models import QuerySet

if TYPE_CHECKING:
    from ..graphql.core.context import SaleorContext
    from ..marketplace.models import Seller
    from ..product.models import Product


def filter_products_by_seller(
    queryset: "QuerySet[Product]",
    seller: Optional["Seller"],
) -> "QuerySet[Product]":
    """Filter products queryset by seller.

    If seller is provided, only return products belonging to that seller.
    Products without a seller are excluded when filtering by a specific seller.
    """
    if seller:
        return queryset.filter(seller=seller)
    return queryset


def filter_products_by_context_seller(
    queryset: "QuerySet[Product]",
    context: "SaleorContext",
) -> "QuerySet[Product]":
    """Filter products queryset by seller from GraphQL context.

    This enables tenant isolation - when accessing a seller-specific storefront,
    only that seller's products are returned.
    """
    from .context import get_seller_from_context

    seller = get_seller_from_context(context)
    return filter_products_by_seller(queryset, seller)




