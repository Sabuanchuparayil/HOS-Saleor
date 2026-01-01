"""Mutation for creating pricing rules."""

import graphene
from decimal import Decimal

from ...core.doc_category import DOC_CATEGORY_MARKETPLACE
from ...core.mutations import BaseMutation
from ...core.types import MarketplaceError
from saleor.marketplace import models
from ....permission.enums import MarketplacePermissions
from ..enums import PricingTypeEnum
from ..types import PricingRule


class PricingRuleCreate(BaseMutation):
    """Create a pricing rule for products."""

    class Arguments:
        product_id = graphene.ID(description="ID of the product (optional).")
        seller_id = graphene.ID(description="ID of the seller (optional, for seller-wide rules).")
        pricing_type = PricingTypeEnum(required=True, description="Type of pricing rule.")
        discount_percentage = graphene.Decimal(description="Discount percentage (if applicable).")
        fixed_price = graphene.Decimal(description="Fixed price override (if applicable).")
        valid_from = graphene.DateTime(description="Start date for seasonal/promotional pricing.")
        valid_until = graphene.DateTime(description="End date for seasonal/promotional pricing.")
        country = graphene.String(description="Country code (optional, for country-specific pricing).")
        is_active = graphene.Boolean(default=True, description="Whether this pricing rule is active.")

    pricing_rule = graphene.Field(PricingRule, description="The created pricing rule.")

    class Meta:
        description = "Create a pricing rule for products."
        doc_category = DOC_CATEGORY_MARKETPLACE
        permissions = (MarketplacePermissions.MANAGE_FINANCE,)
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(
        cls,
        _root,
        info,
        pricing_type,
        product_id=None,
        seller_id=None,
        discount_percentage=None,
        fixed_price=None,
        valid_from=None,
        valid_until=None,
        country=None,
        is_active=True,
    ):
        """Create pricing rule."""
        # Validate that at least one of product_id or seller_id is provided
        from django.core.exceptions import ValidationError
        if not product_id and not seller_id:
            raise ValidationError(
                {
                    "product_id": ValidationError(
                        "Either product_id or seller_id must be provided.",
                        code="REQUIRED",
                    )
                }
            )

        product = None
        seller = None

        if product_id:
            from ....graphql.product.types import Product
            product = cls.get_node_or_error(
                info, product_id, only_type=Product, field="product_id"
            )

        if seller_id:
            from ..types import Seller
            seller = cls.get_node_or_error(
                info, seller_id, only_type=Seller, field="seller_id"
            )

        # Convert enum value to model value
        pricing_type_value = pricing_type.value if hasattr(pricing_type, 'value') else pricing_type

        # Create pricing rule
        pricing_rule = models.PricingRule.objects.create(
            product=product,
            seller=seller,
            pricing_type=pricing_type_value,
            discount_percentage=discount_percentage,
            fixed_price=fixed_price,
            valid_from=valid_from,
            valid_until=valid_until,
            country=country,
            is_active=is_active,
        )

        return cls(pricing_rule=pricing_rule)

