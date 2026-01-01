"""DataLoaders for marketplace models."""

from uuid import UUID

from ..graphql.core.dataloaders import DataLoader
from .models import Seller


class SellerByIdLoader(DataLoader[UUID, Seller]):
    """DataLoader for loading Seller by ID."""

    context_key = "seller_by_id"

    def batch_load(self, keys):
        sellers = Seller.objects.using(self.database_connection_name).filter(
            id__in=keys
        )
        seller_map = {seller.id: seller for seller in sellers}
        return [seller_map.get(seller_id) for seller_id in keys]


class SellerBySlugLoader(DataLoader[str, Seller]):
    """DataLoader for loading Seller by slug."""

    context_key = "seller_by_slug"

    def batch_load(self, keys):
        sellers = Seller.objects.using(self.database_connection_name).filter(
            slug__in=keys
        )
        seller_map = {seller.slug: seller for seller in sellers}
        return [seller_map.get(slug) for slug in keys]


class SellerByDomainLoader(DataLoader[str, Seller]):
    """DataLoader for loading Seller by domain."""

    context_key = "seller_by_domain"

    def batch_load(self, keys):
        from .models import SellerDomain

        domains = (
            SellerDomain.objects.using(self.database_connection_name)
            .filter(domain__in=keys, status="active")
            .select_related("seller")
        )
        domain_map = {domain.domain.lower(): domain.seller for domain in domains}
        return [domain_map.get(domain.lower()) for domain in keys]
