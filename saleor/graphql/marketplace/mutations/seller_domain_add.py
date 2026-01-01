"""GraphQL mutation for adding a domain to a seller."""

import graphene
from django.core.exceptions import ValidationError

from ...core.context import get_database_connection_name
from saleor.marketplace import error_codes, models
from saleor.permission.enums import MarketplacePermissions
from ...core import ResolveInfo
from ...core.mutations import BaseMutation
from ...core.types import MarketplaceError
from ...core.utils import from_global_id_or_error
from ..inputs import SellerDomainInput
from ..types import Seller, SellerDomain


class SellerDomainAdd(BaseMutation):
    """Add a domain to a seller."""

    class Arguments:
        seller_id = graphene.ID(
            required=True, description="ID of the seller to add domain to."
        )
        input = SellerDomainInput(
            required=True, description="Domain information to add."
        )

    seller = graphene.Field(Seller, description="The seller with the new domain.")
    domain = graphene.Field(
        SellerDomain, description="The newly added domain."
    )

    class Meta:
        description = "Adds a domain to a seller's storefront."
        permissions = (MarketplacePermissions.MANAGE_SELLERS,)
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def clean_input(cls, info: ResolveInfo, data):
        """Clean and validate input data."""
        domain = data.get("domain", "").strip().lower()
        if not domain:
            raise ValidationError(
                {
                    "domain": ValidationError(
                        "Domain is required.", code=error_codes.MarketplaceErrorCode.REQUIRED
                    )
                }
            )

        # Basic domain validation
        if not domain or len(domain) > 255:
            raise ValidationError(
                {
                    "domain": ValidationError(
                        "Invalid domain format.", code=error_codes.MarketplaceErrorCode.INVALID_DOMAIN
                    )
                }
            )

        # Check if domain already exists
        if models.SellerDomain.objects.filter(domain=domain).exists():
            raise ValidationError(
                {
                    "domain": ValidationError(
                        "Domain is already in use.",
                        code=error_codes.MarketplaceErrorCode.DOMAIN_ALREADY_IN_USE,
                    )
                }
            )

        return data

    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        """Perform the mutation."""
        seller_id = data.get("seller_id")
        input_data = data.get("input", {})

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

        # Clean input
        cleaned_input = cls.clean_input(info, input_data)

        # Create domain
        domain_obj = models.SellerDomain.objects.create(
            seller=seller,
            domain=cleaned_input.get("domain"),
            is_primary=cleaned_input.get("is_primary", False),
            ssl_enabled=cleaned_input.get("ssl_enabled", False),
        )

        # If this is set as primary, unset other primary domains
        if domain_obj.is_primary:
            models.SellerDomain.objects.filter(
                seller=seller, is_primary=True
            ).exclude(id=domain_obj.id).update(is_primary=False)

        return cls(seller=seller, domain=domain_obj)

