"""Automatic order routing to fulfillment centers."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ...order.models import Order
    from ..models import FulfillmentCenter, Seller


def route_order_to_fulfillment_center(
    order: "Order",
    seller: Optional["Seller"] = None,
) -> Optional["FulfillmentCenter"]:
    """Route order to nearest fulfillment center based on inventory and delivery location.

    Args:
        order: The order to route
        seller: The seller (optional, if routing for specific seller)

    Returns:
        FulfillmentCenter instance or None
    """
    from ..models import FulfillmentCenter, OrderRoutingRule

    if not order.shipping_address:
        return None

    delivery_country = order.shipping_address.country

    # Get active routing rules, ordered by priority
    routing_rules = OrderRoutingRule.objects.filter(is_active=True).order_by("priority")

    # Check each rule's conditions
    for rule in routing_rules:
        conditions = rule.conditions or {}

        # Check country match
        if "countries" in conditions:
            if delivery_country.code not in conditions["countries"]:
                continue

        # Check inventory availability (if specified)
        if "require_inventory" in conditions and conditions["require_inventory"]:
            # Check if fulfillment center has inventory for order lines
            # This would require checking warehouse stock
            # For now, skip this check
            pass

        # Check seller preference (if specified)
        if seller and "seller_ids" in conditions:
            if str(seller.id) not in conditions["seller_ids"]:
                continue

        # Rule matches, return this fulfillment center
        return rule.fulfillment_center

    # If seller has primary fulfillment center, use that
    if seller:
        try:
            logistics_config = seller.logistics_config
            if logistics_config.primary_fulfillment_center:
                return logistics_config.primary_fulfillment_center
        except AttributeError:
            pass

    # Default: return first active fulfillment center
    return FulfillmentCenter.objects.filter(is_active=True).first()


def split_order_by_fulfillment_center(order: "Order") -> dict:
    """Split order lines by fulfillment center based on routing rules.

    Args:
        order: The order to split

    Returns:
        Dictionary mapping fulfillment center to list of order lines
    """
    from collections import defaultdict

    from ..models import FulfillmentCenter

    lines_by_center = defaultdict(list)

    for line in order.lines.all():
        # Get seller for this line
        seller = getattr(line, "seller", None)
        if not seller:
            # No seller, skip routing
            continue

        # Route to fulfillment center
        center = route_order_to_fulfillment_center(order, seller=seller)
        if center:
            lines_by_center[center].append(line)

    return dict(lines_by_center)

