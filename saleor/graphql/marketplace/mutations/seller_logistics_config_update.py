"""Mutation for updating seller logistics configuration."""

import graphene

from ...core.doc_category import DOC_CATEGORY_MARKETPLACE
from ...core.mutations import BaseMutation
from ...core.types import MarketplaceError
from saleor.marketplace import models
from ...permission.enums import MarketplacePermissions
from ..enums import FulfillmentMethodEnum
from ..types import SellerLogisticsConfig


class SellerLogisticsConfigUpdate(BaseMutation):
    """Update seller logistics configuration."""

    class Arguments:
        seller_id = graphene.ID(required=True, description="ID of the seller.")
        fulfillment_method = FulfillmentMethodEnum(description="Fulfillment method.")
        primary_fulfillment_center_id = graphene.ID(
            description="Primary fulfillment center ID."
        )
        shipping_provider = graphene.String(description="Shipping provider name.")
        handling_time_days = graphene.Int(description="Handling time in days.")
        free_shipping_threshold = graphene.Decimal(description="Free shipping threshold.")
        custom_shipping_methods = graphene.JSONString(description="Custom shipping methods (JSON).")
        logistics_partner_integration = graphene.JSONString(
            description="Logistics partner integration config (JSON)."
        )

    logistics_config = graphene.Field(SellerLogisticsConfig, description="Updated logistics config.")

    class Meta:
        description = "Update seller logistics configuration."
        doc_category = DOC_CATEGORY_MARKETPLACE
        permissions = (MarketplacePermissions.MANAGE_FULFILLMENT,)
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(
        cls,
        _root,
        info,
        seller_id,
        fulfillment_method=None,
        primary_fulfillment_center_id=None,
        shipping_provider=None,
        handling_time_days=None,
        free_shipping_threshold=None,
        custom_shipping_methods=None,
        logistics_partner_integration=None,
    ):
        """Update logistics configuration."""
        from ..types import Seller

        seller = cls.get_node_or_error(info, seller_id, only_type=Seller, field="seller_id")

        # Get or create logistics config
        logistics_config, created = models.SellerLogisticsConfig.objects.get_or_create(
            seller=seller
        )

        # Update fields
        if fulfillment_method is not None:
            logistics_config.fulfillment_method = fulfillment_method
        if primary_fulfillment_center_id is not None:
            from ..types import FulfillmentCenter
            fulfillment_center = cls.get_node_or_error(
                info,
                primary_fulfillment_center_id,
                only_type=FulfillmentCenter,
                field="primary_fulfillment_center_id",
            )
            logistics_config.primary_fulfillment_center = fulfillment_center
        if shipping_provider is not None:
            logistics_config.shipping_provider = shipping_provider
        if handling_time_days is not None:
            logistics_config.handling_time_days = handling_time_days
        if free_shipping_threshold is not None:
            logistics_config.free_shipping_threshold = free_shipping_threshold
        if custom_shipping_methods is not None:
            logistics_config.custom_shipping_methods = custom_shipping_methods
        if logistics_partner_integration is not None:
            logistics_config.logistics_partner_integration = logistics_partner_integration

        logistics_config.save()

        return cls(logistics_config=logistics_config)


