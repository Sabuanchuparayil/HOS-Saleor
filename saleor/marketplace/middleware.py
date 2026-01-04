"""Middleware for marketplace multi-tenancy."""

from typing import TYPE_CHECKING, Optional

from django.http import HttpRequest, HttpResponse
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin

if TYPE_CHECKING:
    from ..marketplace.models import Seller


SELLER_LOOKUP_CACHE_TTL_SECONDS = 300  # 5 minutes


class SellerTenantMiddleware(MiddlewareMixin):
    """Middleware to resolve seller from request domain/subdomain.

    This middleware extracts the seller from the request's Host header
    by matching against SellerDomain records. The resolved seller is
    attached to the request object for use in views and GraphQL resolvers.
    """

    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Resolve seller from domain and attach to request."""
        # Get host from request
        host = request.get_host()
        if not host:
            return None

        # Remove port if present
        host = host.split(":")[0].strip().lower()

        cache_key = f"marketplace:seller_by_host:{host}"
        _MISSING = object()
        cached = cache.get(cache_key, _MISSING)
        if cached is not _MISSING:
            # We cache "no seller" as an empty string to allow negative caching.
            if cached == "":
                request.marketplace_seller = None  # type: ignore[attr-defined]
                return None
            from ..marketplace.models import Seller

            request.marketplace_seller = (
                Seller.objects.filter(pk=cached, status="active").first()
            )  # type: ignore[attr-defined]
            return None

        # Import here to avoid circular imports
        from ..marketplace.models import Seller, SellerDomain

        # Try to find seller by domain (exact match or subdomain)
        seller = None

        # First, try exact domain match (only primary domains for reliable multi-tenancy)
        try:
            from ..marketplace.models import SellerDomainStatus
            
            domain_obj = SellerDomain.objects.select_related("seller").filter(
                domain=host, status=SellerDomainStatus.ACTIVE, is_primary=True
            ).first()
            if domain_obj:
                seller = domain_obj.seller
        except Exception:
            pass

        # If no exact match, try subdomain matching
        if not seller:
            # Extract subdomain (e.g., "seller1.example.com" -> "seller1")
            parts = host.split(".")
            if len(parts) >= 3:
                subdomain = parts[0]
                try:
                    # Try to find seller by slug matching subdomain
                    seller = Seller.objects.filter(
                        slug=subdomain, status="active"
                    ).first()
                except Exception:
                    pass

        # Attach seller to request
        request.marketplace_seller = seller  # type: ignore[attr-defined]
        cache.set(cache_key, seller.pk if seller else "", SELLER_LOOKUP_CACHE_TTL_SECONDS)

        return None


def get_request_seller(request: HttpRequest) -> Optional["Seller"]:
    """Get seller from request context (set by SellerTenantMiddleware)."""
    return getattr(request, "marketplace_seller", None)


def set_request_seller(request: HttpRequest, seller: Optional["Seller"]) -> None:
    """Set seller on request context."""
    request.marketplace_seller = seller  # type: ignore[attr-defined]

