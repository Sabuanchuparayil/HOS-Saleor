"""Mutation for requesting inventory synchronization."""

import graphene
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from ...core.doc_category import DOC_CATEGORY_MARKETPLACE
from ...core.mutations import BaseMutation
from ...core.types import MarketplaceError
from saleor.marketplace import models
from saleor.marketplace.context import get_seller_from_context
from saleor.permission.enums import MarketplacePermissions
from ...utils import get_user_or_app_from_context
from ..types_inventory import InventorySync


class InventorySyncRequest(BaseMutation):
    """Request inventory synchronization for a product variant."""

    class Arguments:
        product_variant_id = graphene.ID(
            required=True, description="ID of the product variant to sync."
        )
        fulfillment_center_id = graphene.ID(
            required=False, description="ID of the fulfillment center (optional)."
        )
        warehouse_id = graphene.ID(
            required=False, description="ID of the warehouse (optional)."
        )

    inventory_sync = graphene.Field(
        InventorySync, description="The created inventory sync record."
    )

    class Meta:
        description = "Request inventory synchronization for a product variant."
        doc_category = DOC_CATEGORY_MARKETPLACE
        permissions = (MarketplacePermissions.MANAGE_FULFILLMENT,)
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(
        cls,
        _root,
        info,
        product_variant_id,
        fulfillment_center_id=None,
        warehouse_id=None,
    ):
        """Request inventory sync."""
        from ...product.models import ProductVariant
        from ...warehouse.models import Warehouse, Stock
        from ...core.utils import from_global_id_or_error
        from ..types import FulfillmentCenter

        # Get product variant
        _, variant_pk = from_global_id_or_error(
            product_variant_id, ProductVariant
        )
        variant = ProductVariant.objects.filter(id=variant_pk).first()
        if not variant:
            raise ValidationError(
                {
                    "product_variant_id": ValidationError(
                        "Product variant not found.",
                        code="NOT_FOUND",
                    )
                }
            )

        # Check permissions - seller must own the product
        seller = get_seller_from_context(info.context)
        user_or_app = get_user_or_app_from_context(info.context)

        if not seller and user_or_app:
            seller = models.Seller.objects.filter(owner=user_or_app).first()

        if seller and variant.product.seller_id != seller.id:
            if not user_or_app or not user_or_app.is_staff:
                raise PermissionDenied(
                    permissions=[MarketplacePermissions.MANAGE_FULFILLMENT],
                    message="You can only sync inventory for your own products.",
                )

        # Get fulfillment center
        fulfillment_center = None
        if fulfillment_center_id:
            _, fc_pk = from_global_id_or_error(
                fulfillment_center_id, FulfillmentCenter
            )
            fulfillment_center = models.FulfillmentCenter.objects.filter(
                id=fc_pk
            ).first()
            if not fulfillment_center:
                raise ValidationError(
                    {
                        "fulfillment_center_id": ValidationError(
                            "Fulfillment center not found.",
                            code="NOT_FOUND",
                        )
                    }
                )

        # Get warehouse
        warehouse = None
        if warehouse_id:
            _, warehouse_pk = from_global_id_or_error(warehouse_id, Warehouse)
            warehouse = Warehouse.objects.filter(id=warehouse_pk).first()
            if not warehouse:
                raise ValidationError(
                    {
                        "warehouse_id": ValidationError(
                            "Warehouse not found.",
                            code="NOT_FOUND",
                        )
                    }
                )

        # If no fulfillment center or warehouse specified, try to get from seller's logistics config
        if not fulfillment_center and seller:
            try:
                logistics_config = seller.logistics_config
                if logistics_config.primary_fulfillment_center:
                    fulfillment_center = logistics_config.primary_fulfillment_center
            except models.SellerLogisticsConfig.DoesNotExist:
                pass

        if not fulfillment_center:
            raise ValidationError(
                {
                    "fulfillment_center_id": ValidationError(
                        "Fulfillment center is required. Please specify one or configure seller logistics.",
                        code="REQUIRED",
                    )
                }
            )

        # Get stock quantity from warehouse
        quantity_available = 0
        quantity_reserved = 0

        if warehouse:
            stock = Stock.objects.filter(
                product_variant=variant, warehouse=warehouse
            ).first()
            if stock:
                quantity_available = stock.quantity - stock.quantity_allocated
                quantity_reserved = stock.quantity_allocated
        else:
            # Get from all warehouses in fulfillment center
            # Note: FulfillmentCenter may not have direct warehouse relationship
            # For now, get from all warehouses if available
            stocks = Stock.objects.filter(product_variant=variant)
            if stocks.exists():
                quantity_available = sum(
                    stock.quantity - stock.quantity_allocated for stock in stocks
                )
                quantity_reserved = sum(
                    stock.quantity_allocated for stock in stocks
                )

        # Create inventory sync record
        inventory_sync = models.InventorySync.objects.create(
            product_variant=variant,
            fulfillment_center=fulfillment_center,
            warehouse=warehouse,
            quantity_available=quantity_available,
            quantity_reserved=quantity_reserved,
            synced_at=timezone.now(),
        )

        return cls(inventory_sync=inventory_sync)

