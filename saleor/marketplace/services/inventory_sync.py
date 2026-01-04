"""Real-time inventory synchronization service."""

from typing import TYPE_CHECKING, Optional

from django.db import transaction
from django.utils import timezone

if TYPE_CHECKING:
    from ...product.models import ProductVariant
    from ...warehouse.models import Warehouse
    from ..models import FulfillmentCenter, InventorySync


def sync_inventory_for_variant(
    variant: "ProductVariant",
    fulfillment_center: Optional["FulfillmentCenter"] = None,
    warehouse: Optional["Warehouse"] = None,
    sync_method: str = "polling",
) -> "InventorySync":
    """Sync inventory for a product variant from warehouse to fulfillment center.

    Args:
        variant: Product variant to sync
        fulfillment_center: Fulfillment center to sync to (optional)
        warehouse: Warehouse to sync from (optional, uses fulfillment center's warehouses if not provided)
        sync_method: Method used for sync (webhook, polling, manual)

    Returns:
        InventorySync instance
    """
    from ..models import FulfillmentCenter, InventorySync

    # If fulfillment center provided, get its warehouses
    if fulfillment_center and not warehouse:
        warehouses = fulfillment_center.warehouses.all()
        if warehouses.exists():
            warehouse = warehouses.first()
    elif not warehouse:
        # No warehouse specified, skip sync
        return None

    # Get stock information from warehouse
    from ...warehouse.models import Stock

    stock = Stock.objects.filter(
        product_variant=variant, warehouse=warehouse
    ).first()

    if not stock:
        quantity_available = 0
        quantity_reserved = 0
    else:
        # "available" should reflect current on-hand quantity, and "reserved"
        # should reflect reserved quantity. Allocation is not availability.
        quantity_available = stock.quantity or 0
        # Calculate reserved quantity from stock reservations (Stock model doesn't have quantity_reserved)
        from ...warehouse.models import Reservation
        from django.db.models import Sum
        from django.db.models.functions import Coalesce
        
        quantity_reserved = (
            Reservation.objects.filter(stock=stock)
            .filter(reserved_until__gt=timezone.now())
            .aggregate(total=Coalesce(Sum("quantity_reserved"), 0))["total"]
        )

    # Create or update inventory sync record
    with transaction.atomic():
        sync, created = InventorySync.objects.update_or_create(
            product_variant=variant,
            fulfillment_center=fulfillment_center,
            warehouse=warehouse,
            defaults={
                "quantity_available": quantity_available,
                "quantity_reserved": quantity_reserved,
                "synced_at": timezone.now(),
                "sync_method": sync_method,
            },
        )

    return sync


def sync_all_inventory_for_seller(seller, fulfillment_center=None):
    """Sync all inventory for a seller's products.

    Args:
        seller: Seller instance
        fulfillment_center: Fulfillment center to sync to (optional)
    """
    from ..models import FulfillmentCenter

    # Get seller's products
    products = seller.products.all()

    # Get fulfillment center if not provided
    if not fulfillment_center:
        try:
            fulfillment_center = seller.logistics_config.primary_fulfillment_center
        except AttributeError:
            # No logistics config, get first active center
            fulfillment_center = FulfillmentCenter.objects.filter(is_active=True).first()

    if not fulfillment_center:
        return

    # Sync inventory for all variants of seller's products
    for product in products:
        for variant in product.variants.all():
            sync_inventory_for_variant(
                variant, fulfillment_center=fulfillment_center, sync_method="polling"
            )


def get_aggregated_inventory_for_variant(
    variant: "ProductVariant",
) -> dict:
    """Get aggregated inventory across all fulfillment centers for a variant.

    Args:
        variant: Product variant

    Returns:
        Dictionary with aggregated inventory data
    """
    from ..models import InventorySync

    syncs = InventorySync.objects.filter(product_variant=variant)

    total_available = sum(sync.quantity_available for sync in syncs)
    total_reserved = sum(sync.quantity_reserved for sync in syncs)

    return {
        "total_available": total_available,
        "total_reserved": total_reserved,
        "total_quantity": total_available + total_reserved,
        "by_center": {
            (sync.fulfillment_center.name if sync.fulfillment_center else str(sync.fulfillment_center_id)): {
                "available": sync.quantity_available,
                "reserved": sync.quantity_reserved,
            }
            for sync in syncs
        },
    }

