"""Mutation for creating seller shipping methods."""

import graphene

from ...core.doc_category import DOC_CATEGORY_MARKETPLACE
from ...core.mutations import BaseMutation
from ...core.types import MarketplaceError
from ...marketplace import models
from ...marketplace.context import get_seller_from_context
from ...permission.enums import MarketplacePermissions
from ...graphql.utils import get_user_or_app_from_context
from ..inputs import SellerShippingMethodInput
from ..types import SellerShippingMethod


class SellerShippingMethodCreate(BaseMutation):
    """Create a seller-specific shipping method."""

    class Arguments:
        input = SellerShippingMethodInput(
            required=True, description="Fields required to create a shipping method."
        )

    shipping_method = graphene.Field(
        SellerShippingMethod, description="The created shipping method."
    )

    class Meta:
        description = "Create a seller-specific shipping method."
        doc_category = DOC_CATEGORY_MARKETPLACE
        permissions = (MarketplacePermissions.MANAGE_FULFILLMENT,)
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(cls, _root, info, input):
        """Create shipping method."""
        from django.core.exceptions import PermissionDenied, ValidationError

        # Get seller from context or check if user owns a seller
        seller = get_seller_from_context(info.context)
        user_or_app = get_user_or_app_from_context(info.context)

        if not seller and user_or_app:
            seller = models.Seller.objects.filter(owner=user_or_app).first()

        if not seller:
            raise PermissionDenied(
                permissions=[MarketplacePermissions.MANAGE_FULFILLMENT],
                message="You must be a seller to create shipping methods.",
            )

        # Check if seller is active
        if seller.status != models.SellerStatus.ACTIVE:
            raise ValidationError(
                {
                    "seller": ValidationError(
                        "Your seller account must be active to create shipping methods.",
                        code="INVALID",
                    )
                }
            )

        # Create shipping method
        shipping_method = models.SellerShippingMethod(
            seller=seller,
            name=input.get("name"),
            price=input.get("price"),
            estimated_days=input.get("estimated_days"),
            is_active=input.get("is_active", True),
            destination_city=input.get("destination_city"),
            tiered_pricing=input.get("tiered_pricing"),
        )

        # Set fulfillment center if provided
        if fulfillment_center_id := input.get("fulfillment_center_id"):
            from ..types import FulfillmentCenter
            from ...core.utils import from_global_id_or_error

            _, fc_id = from_global_id_or_error(
                fulfillment_center_id, FulfillmentCenter
            )
            shipping_method.fulfillment_center_id = fc_id

        # Set destination country if provided
        if country_code := input.get("destination_country"):
            shipping_method.destination_country = country_code

        shipping_method.save()

        return cls(shipping_method=shipping_method)


