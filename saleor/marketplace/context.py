"""Context utilities for marketplace multi-tenancy."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..graphql.core.context import SaleorContext
    from ..marketplace.models import Seller


def get_seller_from_context(context: "SaleorContext") -> Optional["Seller"]:
    """Get seller from GraphQL context.

    The seller is set by SellerTenantMiddleware from the request domain.
    """
    if hasattr(context, "request"):
        from .middleware import get_request_seller

        return get_request_seller(context.request)
    return None


def set_seller_in_context(context: "SaleorContext", seller: Optional["Seller"]) -> None:
    """Set seller in GraphQL context."""
    if hasattr(context, "request"):
        from .middleware import set_request_seller

        set_request_seller(context.request, seller)




