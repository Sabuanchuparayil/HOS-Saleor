"""Mutation for updating B2B seller credit terms."""

import graphene

from ...core.doc_category import DOC_CATEGORY_MARKETPLACE
from ...core.mutations import BaseMutation
from ...core.types import MarketplaceError
from ...marketplace import models
from ...marketplace.context import get_seller_from_context
from ...permission.enums import MarketplacePermissions
from ...graphql.utils import get_user_or_app_from_context
from ..types import Seller


class SellerCreditTermsUpdateInput(graphene.InputObjectType):
    """Input for updating seller credit terms."""

    minimum_order_quantity = graphene.Int(
        description="Minimum order quantity for B2B sellers."
    )
    credit_terms_enabled = graphene.Boolean(
        description="Whether credit terms are enabled for B2B sellers."
    )

    class Meta:
        doc_category = DOC_CATEGORY_MARKETPLACE


class SellerCreditTermsUpdate(BaseMutation):
    """Update B2B seller credit terms and minimum order quantities."""

    class Arguments:
        seller_id = graphene.ID(required=True, description="ID of the seller.")
        input = SellerCreditTermsUpdateInput(
            required=True, description="Fields required to update credit terms."
        )

    seller = graphene.Field(Seller, description="The updated seller.")

    class Meta:
        description = "Update B2B seller credit terms and minimum order quantities."
        doc_category = DOC_CATEGORY_MARKETPLACE
        permissions = (MarketplacePermissions.MANAGE_SELLERS,)
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(cls, _root, info, seller_id, input):
        """Update credit terms."""
        from django.core.exceptions import PermissionDenied, ValidationError

        seller = cls.get_node_or_error(info, seller_id, only_type=Seller, field="seller_id")

        # Check permissions - seller must own this or be staff
        context_seller = get_seller_from_context(info.context)
        user_or_app = get_user_or_app_from_context(info.context)

        if not context_seller and user_or_app:
            context_seller = models.Seller.objects.filter(owner=user_or_app).first()

        if not context_seller or seller.id != context_seller.id:
            if not user_or_app or not user_or_app.is_staff:
                raise PermissionDenied(
                    permissions=[MarketplacePermissions.MANAGE_SELLERS],
                    message="You can only update your own seller credit terms.",
                )

        # Update fields
        if "minimum_order_quantity" in input:
            seller.minimum_order_quantity = input["minimum_order_quantity"]
        if "credit_terms_enabled" in input:
            seller.credit_terms_enabled = input["credit_terms_enabled"]

        seller.save(update_fields=["minimum_order_quantity", "credit_terms_enabled", "updated_at"])

        return cls(seller=seller)


