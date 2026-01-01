"""GraphQL mutation for verifying a seller domain."""

import graphene
from django.core.exceptions import ValidationError
from django.utils import timezone

from ...core.context import get_database_connection_name
from saleor.marketplace import error_codes, models
from ....permission.enums import MarketplacePermissions
from ...core import ResolveInfo
from ...core.mutations import BaseMutation
from ...core.types import MarketplaceError
from ...core.utils import from_global_id_or_error
from ..types import Seller, SellerDomain


class SellerDomainVerify(BaseMutation):
    """Verify a seller domain."""

    class Arguments:
        seller_id = graphene.ID(
            required=True, description="ID of the seller."
        )
        domain_id = graphene.ID(
            required=True, description="ID of the domain to verify."
        )

    seller = graphene.Field(Seller, description="The seller.")
    domain = graphene.Field(SellerDomain, description="The verified domain.")

    class Meta:
        description = "Verifies a seller domain (basic implementation)."
        permissions = (MarketplacePermissions.MANAGE_SELLERS,)
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        """Perform the mutation."""
        seller_id = data.get("seller_id")
        domain_id = data.get("domain_id")

        # Get seller
        _, seller_pk = from_global_id_or_error(seller_id, Seller)
        try:
            seller = models.Seller.objects.using(
                get_database_connection_name(info.context)
            ).get(pk=seller_pk)
        except models.Seller.DoesNotExist:
            raise ValidationError(
                {
                    "seller_id": ValidationError(
                        "Seller not found.", code=error_codes.MarketplaceErrorCode.NOT_FOUND
                    )
                }
            )

        # Get domain
        _, domain_pk = from_global_id_or_error(domain_id, "SellerDomain")
        try:
            domain_obj = models.SellerDomain.objects.using(
                get_database_connection_name(info.context)
            ).get(pk=domain_pk, seller=seller)
        except models.SellerDomain.DoesNotExist:
            raise ValidationError(
                {
                    "domain_id": ValidationError(
                        "Domain not found.", code=error_codes.MarketplaceErrorCode.NOT_FOUND
                    )
                }
            )

        # TODO: Implement actual domain verification (DNS check, TXT record, etc.)
        # For now, we'll just mark it as active and set verified_at
        # In a production system, you would:
        # 1. Check for a TXT record at _saleor-verify.{domain}
        # 2. Verify SSL certificate if SSL is enabled
        # 3. Check that the domain points to the correct server
        domain_obj.status = models.SellerDomainStatus.ACTIVE
        domain_obj.verified_at = timezone.now()
        domain_obj.save(update_fields=["status", "verified_at"])

        return cls(seller=seller, domain=domain_obj)

