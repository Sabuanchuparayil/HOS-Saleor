"""GraphQL types for inventory sync."""

import graphene
from graphene import relay

from saleor.marketplace import models
from ..core.connection import CountableConnection
from ..core.doc_category import DOC_CATEGORY_MARKETPLACE
from ..core.scalars import DateTime
from ..core.types import ModelObjectType
from .types import FulfillmentCenter


class InventorySync(ModelObjectType[models.InventorySync]):
    """Represents an inventory synchronization record."""

    class Meta:
        description = "Inventory synchronization between fulfillment centers and seller dashboards"
        model = models.InventorySync
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    product_variant = graphene.Field(
        "saleor.graphql.product.types.ProductVariant",
        required=True,
        description="Product variant being synced.",
    )
    fulfillment_center = graphene.Field(
        FulfillmentCenter,
        required=True,
        description="Fulfillment center this sync is for.",
    )
    warehouse = graphene.Field(
        "saleor.graphql.warehouse.types.Warehouse",
        required=True,
        description="Warehouse being synced.",
    )
    quantity_available = graphene.Int(
        required=True,
        description="Available quantity at time of sync.",
    )
    quantity_reserved = graphene.Int(
        required=True,
        description="Reserved quantity at time of sync.",
    )
    synced_at = DateTime(
        required=True,
        description="When the sync was performed.",
    )
    sync_method = graphene.String(
        required=True,
        description="Method used for sync (webhook, polling, manual).",
    )
    created_at = DateTime(required=True)
    updated_at = DateTime(required=True)


class InventorySyncCountableConnection(CountableConnection):
    """Connection type for InventorySync list queries."""

    class Meta:
        node = InventorySync
        doc_category = DOC_CATEGORY_MARKETPLACE

