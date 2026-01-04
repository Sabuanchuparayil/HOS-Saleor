"""Seller-type-aware shipping logic and order routing."""

from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from django.db.models import Q

if TYPE_CHECKING:
    from ..account.models import Address
    from ..checkout.models import Checkout
    from ..order.models import Order
    from ..shipping.models import ShippingMethod, ShippingZone
    from .models import FulfillmentCenter, Seller, SellerLogisticsConfig, SellerShippingMethod


def get_applicable_shipping_methods_for_seller(
    seller: "Seller",
    shipping_address: Optional["Address"] = None,
    order_total: Optional[Decimal] = None,
) -> list["ShippingMethod"]:
    """Get applicable shipping methods based on seller type and configuration.

    Args:
        seller: The seller instance
        shipping_address: Customer shipping address (optional)
        order_total: Total order value (optional, for free shipping threshold)

    Returns:
        List of applicable shipping methods
    """
    from ..shipping.models import ShippingMethod

    # Get seller's logistics configuration
    try:
        logistics_config = seller.logistics_config
    except AttributeError:
        # No logistics config, return empty list
        return []

    # Get shipping zones for this seller
    shipping_zones = logistics_config.shipping_zones.all()
    if not shipping_zones.exists():
        # No shipping zones configured, return empty list
        return []

    # Filter shipping methods by zones
    methods = ShippingMethod.objects.filter(shipping_zone__in=shipping_zones)

    # Apply seller-type-specific filtering
    if seller.seller_type == "b2b_wholesale":
        # B2B sellers may have negotiated rates or bulk shipping discounts.
        # SellerShippingMethod is handled in MarketplaceShippingPlugin (external methods).
        # Keep standard methods unchanged here.
        pass

    # Check free shipping threshold
    if (
        logistics_config.free_shipping_threshold
        and order_total
        and order_total >= logistics_config.free_shipping_threshold
    ):
        # Filter to include free shipping methods
        methods = methods.filter(price_amount=0)

    return list(methods)


def calculate_shipping_cost_for_seller(
    seller: "Seller",
    shipping_method: "ShippingMethod",
    weight: Optional[Decimal] = None,
    order_total: Optional[Decimal] = None,
) -> Decimal:
    """Calculate shipping cost for a seller based on seller type and configuration.

    Args:
        seller: The seller instance
        shipping_method: The shipping method to calculate cost for
        weight: Total weight of items (optional, for weight-based calculation)
        order_total: Total order value (optional, for free shipping threshold)

    Returns:
        Shipping cost as Decimal
    """
    from ..shipping.models import ShippingMethod

    # Get seller's logistics configuration
    try:
        logistics_config = seller.logistics_config
    except AttributeError:
        # No logistics config, use standard shipping method price
        return Decimal(str(shipping_method.price_amount or 0))

    # Check free shipping threshold
    if (
        logistics_config.free_shipping_threshold
        and order_total
        and order_total >= logistics_config.free_shipping_threshold
    ):
        return Decimal("0.00")

    # Check for seller-specific shipping method
    from .models import SellerShippingMethod
    seller_method = SellerShippingMethod.objects.filter(
        seller=seller,
        is_active=True,
        # Match by name or other criteria
    ).first()

    if seller_method:
        # Use seller-specific pricing
        base_price = seller_method.price

        # Apply tiered pricing if available
        if seller_method.tiered_pricing and weight:
            # Calculate based on weight tiers
            for tier in seller_method.tiered_pricing.get("weight_tiers", []):
                if weight >= tier.get("min_weight", 0):
                    return Decimal(str(tier.get("price", base_price)))
        elif seller_method.tiered_pricing and order_total:
            # Calculate based on price tiers
            for tier in seller_method.tiered_pricing.get("price_tiers", []):
                if order_total >= Decimal(str(tier.get("min_price", 0))):
                    return Decimal(str(tier.get("price", base_price)))

        return base_price

    # Use standard shipping method price
    return Decimal(str(shipping_method.price_amount or 0))


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
    from .models import FulfillmentCenter, OrderRoutingRule

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

