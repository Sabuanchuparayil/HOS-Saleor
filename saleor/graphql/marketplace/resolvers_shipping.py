"""Resolvers for seller shipping methods."""

from ..core import ResolveInfo
from ..core.context import get_database_connection_name
from ..core.utils import from_global_id_or_error
from saleor.marketplace import models
from saleor.marketplace.context import get_seller_from_context
from ...utils import get_user_or_app_from_context
from .types import SellerShippingMethod


def resolve_seller_shipping_methods(
    info: ResolveInfo,
    seller_id: str | None = None,
    is_active: bool | None = None,
):
    """Resolve shipping methods for a seller."""
    connection_name = get_database_connection_name(info.context)
    qs = models.SellerShippingMethod.objects.using(connection_name).all()

    # Filter by seller
    if seller_id:
        _, seller_pk = from_global_id_or_error(seller_id, "Seller")
        qs = qs.filter(seller_id=seller_pk)
    else:
        # If no seller_id provided, filter by context seller
        seller = get_seller_from_context(info.context)
        if seller:
            qs = qs.filter(seller=seller)
        else:
            # If no seller in context and no seller_id, return empty
            user_or_app = get_user_or_app_from_context(info.context)
            if not user_or_app or not user_or_app.is_staff:
                return models.SellerShippingMethod.objects.using(connection_name).none()

    # Filter by active status
    if is_active is not None:
        qs = qs.filter(is_active=is_active)

    return qs.order_by("name")


def resolve_seller_shipping_method(info: ResolveInfo, id: str):
    """Resolve a shipping method by ID."""
    _, db_id = from_global_id_or_error(id, SellerShippingMethod)
    connection_name = get_database_connection_name(info.context)
    return models.SellerShippingMethod.objects.using(connection_name).filter(
        id=db_id
    ).first()

