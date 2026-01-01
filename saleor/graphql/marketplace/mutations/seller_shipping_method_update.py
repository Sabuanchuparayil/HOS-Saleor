"""Mutation for updating seller shipping methods."""

import graphene

from ...core.doc_category import DOC_CATEGORY_MARKETPLACE
from ...core.mutations import BaseMutation
from ...core.types import MarketplaceError
from saleor.marketplace import models
from saleor.marketplace.context import get_seller_from_context
from saleor.permission.enums import MarketplacePermissions
from ..utils import get_user_or_app_from_context
from ..inputs import SellerShippingMethodInput
from ..types import SellerShippingMethod


class SellerShippingMethodUpdateInput(SellerShippingMethodInput):
    """Input type for updating a shipping method (all fields optional)."""

    name = graphene.String(description="Name of the shipping method.")
    price = graphene.Decimal(description="Shipping price.")
    estimated_days = graphene.Int(description="Estimated delivery time in days.")
    is_active = graphene.Boolean(description="Whether this shipping method is active.")
    fulfillment_center_id = graphene.ID(description="ID of the fulfillment center.")
    destination_country = graphene.String(
        description="Destination country code (ISO 3166-1 alpha-2)."
    )
    destination_city = graphene.String(description="Destination city.")
    tiered_pricing = graphene.JSONString(description="Tiered pricing configuration (JSON).")

    class Meta:
        doc_category = DOC_CATEGORY_MARKETPLACE


class SellerShippingMethodUpdate(BaseMutation):
    """Update a seller-specific shipping method."""

    class Arguments:
        id = graphene.ID(required=True, description="ID of the shipping method to update.")
        input = SellerShippingMethodUpdateInput(
            required=True, description="Fields required to update a shipping method."
        )

    shipping_method = graphene.Field(
        SellerShippingMethod, description="The updated shipping method."
    )

    class Meta:
        description = "Update a seller-specific shipping method."
        doc_category = DOC_CATEGORY_MARKETPLACE
        permissions = (MarketplacePermissions.MANAGE_FULFILLMENT,)
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(cls, _root, info, id, input):
        """Update shipping method."""
        from django.core.exceptions import PermissionDenied, ValidationError

        shipping_method = cls.get_node_or_error(
            info, id, only_type=SellerShippingMethod, field="id"
        )

        # Check permissions - seller must own this shipping method
        seller = get_seller_from_context(info.context)
        user_or_app = get_user_or_app_from_context(info.context)

        if not seller and user_or_app:
            seller = models.Seller.objects.filter(owner=user_or_app).first()

        if not seller or shipping_method.seller_id != seller.id:
            # Check if user is staff
            if not user_or_app or not user_or_app.is_staff:
                raise PermissionDenied(
                    permissions=[MarketplacePermissions.MANAGE_FULFILLMENT],
                    message="You can only update your own shipping methods.",
                )

        # Update fields
        if "name" in input:
            shipping_method.name = input["name"]
        if "price" in input:
            shipping_method.price = input["price"]
        if "estimated_days" in input:
            shipping_method.estimated_days = input.get("estimated_days")
        if "is_active" in input:
            shipping_method.is_active = input["is_active"]
        if "destination_city" in input:
            shipping_method.destination_city = input.get("destination_city")
        if "tiered_pricing" in input:
            shipping_method.tiered_pricing = input.get("tiered_pricing")

        # Update fulfillment center if provided
        if "fulfillment_center_id" in input and input["fulfillment_center_id"]:
            from ..types import FulfillmentCenter
            from ...core.utils import from_global_id_or_error

            _, fc_id = from_global_id_or_error(
                input["fulfillment_center_id"], FulfillmentCenter
            )
            shipping_method.fulfillment_center_id = fc_id
        elif "fulfillment_center_id" in input and input["fulfillment_center_id"] is None:
            shipping_method.fulfillment_center = None

        # Update destination country if provided
        if "destination_country" in input:
            shipping_method.destination_country = input.get("destination_country")

        shipping_method.save()

        return cls(shipping_method=shipping_method)


