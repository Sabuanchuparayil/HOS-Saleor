"""GraphQL mutation for removing a domain from a seller."""

import graphene
from django.core.exceptions import ValidationError

from ...core.context import get_database_connection_name
from ....marketplace import error_codes, models
from ....permission.enums import MarketplacePermissions
from ...core import ResolveInfo
from ...core.mutations import BaseMutation
from ...core.types import MarketplaceError
from ...core.utils import from_global_id_or_error
from ..types import Seller


class SellerDomainRemove(BaseMutation):
    """Remove a domain from a seller."""

    class Arguments:
        seller_id = graphene.ID(
            required=True, description="ID of the seller to remove domain from."
        )
        domain_id = graphene.ID(
            required=True, description="ID of the domain to remove."
        )

    seller = graphene.Field(Seller, description="The seller with the domain removed.")

    class Meta:
        description = "Removes a domain from a seller's storefront."
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

        # Delete domain
        domain_obj.delete()

        return cls(seller=seller)

