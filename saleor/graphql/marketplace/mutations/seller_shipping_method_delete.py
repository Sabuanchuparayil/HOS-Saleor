"""Mutation for deleting seller shipping methods."""

import graphene

from ...core.doc_category import DOC_CATEGORY_MARKETPLACE
from ...core.mutations import BaseMutation, ModelDeleteMutation
from ...core.types import MarketplaceError
from ...marketplace import models
from ...marketplace.context import get_seller_from_context
from ...permission.enums import MarketplacePermissions
from ...graphql.utils import get_user_or_app_from_context
from ..types import SellerShippingMethod


class SellerShippingMethodDelete(ModelDeleteMutation):
    """Delete a seller-specific shipping method."""

    class Arguments:
        id = graphene.ID(required=True, description="ID of the shipping method to delete.")

    class Meta:
        description = "Delete a seller-specific shipping method."
        model = models.SellerShippingMethod
        object_type = SellerShippingMethod
        doc_category = DOC_CATEGORY_MARKETPLACE
        permissions = (MarketplacePermissions.MANAGE_FULFILLMENT,)
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(cls, _root, info, id):
        """Delete shipping method with permission check."""
        from django.core.exceptions import PermissionDenied

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
                    message="You can only delete your own shipping methods.",
                )

        return super().perform_mutation(_root, info, id)


