"""Resolvers for inventory sync."""

from typing import Optional

from ..core import ResolveInfo
from ..core.context import get_database_connection_name
from ..core.utils import from_global_id_or_error
from ...marketplace import models
from ...marketplace.context import get_seller_from_context
from ...graphql.utils import get_user_or_app_from_context
from .types_inventory import InventorySync


def resolve_inventory_syncs(
    info: ResolveInfo,
    product_variant_id: Optional[str] = None,
    fulfillment_center_id: Optional[str] = None,
    warehouse_id: Optional[str] = None,
):
    """Resolve inventory syncs with optional filtering."""
    connection_name = get_database_connection_name(info.context)
    qs = models.InventorySync.objects.using(connection_name).all()

    # Filter by product variant
    if product_variant_id:
        from ...product.models import ProductVariant
        _, variant_pk = from_global_id_or_error(product_variant_id, ProductVariant)
        qs = qs.filter(product_variant_id=variant_pk)

    # Filter by fulfillment center
    if fulfillment_center_id:
        from .types import FulfillmentCenter
        _, fc_pk = from_global_id_or_error(fulfillment_center_id, FulfillmentCenter)
        qs = qs.filter(fulfillment_center_id=fc_pk)

    # Filter by warehouse
    if warehouse_id:
        from ...warehouse.models import Warehouse
        _, warehouse_pk = from_global_id_or_error(warehouse_id, Warehouse)
        qs = qs.filter(warehouse_id=warehouse_pk)

    # Filter by seller if in context (sellers can only see their own product syncs)
    seller = get_seller_from_context(info.context)
    user_or_app = get_user_or_app_from_context(info.context)
    if seller and not (user_or_app and user_or_app.is_staff):
        # Filter to only products owned by this seller
        qs = qs.filter(product_variant__product__seller=seller)

    return qs.order_by("-synced_at", "-created_at")


def resolve_inventory_sync(info: ResolveInfo, id: str):
    """Resolve an inventory sync by ID."""
    _, db_id = from_global_id_or_error(id, InventorySync)
    connection_name = get_database_connection_name(info.context)
    return models.InventorySync.objects.using(connection_name).filter(
        id=db_id
    ).first()


