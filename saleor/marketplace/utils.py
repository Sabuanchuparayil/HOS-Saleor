"""Utility functions for marketplace functionality."""

from collections import defaultdict
from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import models
from django.db.models import QuerySet, Sum

if TYPE_CHECKING:
    from ..checkout.models import CheckoutLine
    from ..marketplace.models import SellerSettlement
    from ..order.models import Order, OrderLine


def group_lines_by_seller(lines: list["OrderLine"] | list["CheckoutLine"]) -> dict:
    """Group order lines or checkout lines by seller.

    Returns a dictionary mapping seller to list of lines.
    Lines without a seller are grouped under None.
    """
    grouped = defaultdict(list)
    for line in lines:
        seller = getattr(line, "seller", None)
        if hasattr(line, "product") and line.product:
            seller = getattr(line.product, "seller", seller)
        grouped[seller].append(line)
    return dict(grouped)


def allocate_shipping_cost_by_seller(
    lines_by_seller: dict,
    total_shipping_cost: Decimal,
    allocation_method: str = "proportional",
) -> dict:
    """Allocate shipping cost across sellers based on allocation method and seller type.

    Args:
        lines_by_seller: Dictionary mapping seller to list of lines
        total_shipping_cost: Total shipping cost to allocate
        allocation_method: Method to use for allocation
            - "proportional": Allocate based on line total value proportion
            - "equal": Split equally among all sellers
            - "weight": Allocate based on total weight (requires weight on lines)

    Returns:
        Dictionary mapping seller to allocated shipping cost
    """
    if not lines_by_seller:
        return {}

    allocation = {}

    # Consider seller type for B2B negotiated rates or bulk discounts
    seller_type_adjustments = {}
    for seller in lines_by_seller:
        if seller and seller.seller_type == "b2b_wholesale":
            # B2B sellers may have negotiated rates or bulk shipping discounts
            # Check logistics config for custom shipping rates
            try:
                logistics_config = seller.logistics_config
                # B2B sellers often have negotiated bulk shipping rates
                # Apply discount factor if configured (e.g., 0.9 for 10% discount)
                # For now, use standard allocation but structure is ready for discounts
                discount_factor = Decimal("1.0")
                if hasattr(logistics_config, "custom_shipping_methods"):
                    # Check for B2B bulk shipping discount in custom methods
                    custom_methods = logistics_config.custom_shipping_methods or {}
                    if isinstance(custom_methods, dict):
                        b2b_discount = custom_methods.get("b2b_discount_factor", 1.0)
                        discount_factor = Decimal(str(b2b_discount))
                seller_type_adjustments[seller] = discount_factor
            except AttributeError:
                seller_type_adjustments[seller] = Decimal("1.0")
        else:
            # B2C sellers use standard rates
            seller_type_adjustments[seller] = Decimal("1.0")

    if allocation_method == "equal":
        cost_per_seller = total_shipping_cost / len(lines_by_seller)
        for seller in lines_by_seller:
            # Apply seller type adjustment
            adjustment = seller_type_adjustments.get(seller, Decimal("1.0"))
            allocation[seller] = cost_per_seller * adjustment
    elif allocation_method == "proportional":
        # Calculate total value per seller
        seller_totals = {}
        grand_total = Decimal("0")
        for seller, lines in lines_by_seller.items():
            seller_total = sum(
                line.total_price.gross.amount if hasattr(line, "total_price") else line.get_total().gross.amount
                for line in lines
            )
            seller_totals[seller] = seller_total
            grand_total += seller_total

        # Allocate proportionally
        if grand_total > 0:
            for seller, seller_total in seller_totals.items():
                proportion = seller_total / grand_total
                base_allocation = total_shipping_cost * proportion
                # Apply seller type adjustment
                adjustment = seller_type_adjustments.get(seller, Decimal("1.0"))
                allocation[seller] = base_allocation * adjustment
        else:
            # If no totals, split equally
            cost_per_seller = total_shipping_cost / len(lines_by_seller)
            for seller in lines_by_seller:
                adjustment = seller_type_adjustments.get(seller, Decimal("1.0"))
                allocation[seller] = cost_per_seller * adjustment
    elif allocation_method == "weight":
        # Calculate total weight per seller
        seller_weights = {}
        total_weight = Decimal("0")
        for seller, lines in lines_by_seller.items():
            seller_weight = Decimal("0")
            for line in lines:
                if hasattr(line, "variant") and line.variant and line.variant.weight:
                    seller_weight += line.variant.weight.value * line.quantity
            seller_weights[seller] = seller_weight
            total_weight += seller_weight

        # Allocate based on weight
        if total_weight > 0:
            for seller, weight in seller_weights.items():
                proportion = weight / total_weight
                base_allocation = total_shipping_cost * proportion
                # Apply seller type adjustment
                adjustment = seller_type_adjustments.get(seller, Decimal("1.0"))
                allocation[seller] = base_allocation * adjustment
        else:
            # If no weights, split equally
            cost_per_seller = total_shipping_cost / len(lines_by_seller)
            for seller in lines_by_seller:
                allocation[seller] = cost_per_seller
    else:
        raise ValueError(f"Unknown allocation method: {allocation_method}")

    return allocation


def allocate_discount_by_seller(
    lines_by_seller: dict,
    total_discount: Decimal,
    allocation_method: str = "proportional",
) -> dict:
    """Allocate discount amount across sellers based on allocation method.

    Args:
        lines_by_seller: Dictionary mapping seller to list of lines
        total_discount: Total discount amount to allocate
        allocation_method: Method to use for allocation
            - "proportional": Allocate based on line total value proportion
            - "equal": Split equally among all sellers

    Returns:
        Dictionary mapping seller to allocated discount amount
    """
    if not lines_by_seller:
        return {}

    allocation = {}

    if allocation_method == "equal":
        discount_per_seller = total_discount / len(lines_by_seller)
        for seller in lines_by_seller:
            allocation[seller] = discount_per_seller
    elif allocation_method == "proportional":
        # Calculate total value per seller
        seller_totals = {}
        grand_total = Decimal("0")
        for seller, lines in lines_by_seller.items():
            seller_total = sum(
                line.total_price.gross.amount if hasattr(line, "total_price") else line.get_total().gross.amount
                for line in lines
            )
            seller_totals[seller] = seller_total
            grand_total += seller_total

        # Allocate proportionally
        if grand_total > 0:
            for seller, seller_total in seller_totals.items():
                proportion = seller_total / grand_total
                allocation[seller] = total_discount * proportion
        else:
            # If no totals, split equally
            discount_per_seller = total_discount / len(lines_by_seller)
            for seller in lines_by_seller:
                allocation[seller] = discount_per_seller
    else:
        raise ValueError(f"Unknown allocation method: {allocation_method}")

    return allocation


def calculate_seller_subtotal(lines: list["OrderLine"] | list["CheckoutLine"]) -> Decimal:
    """Calculate the subtotal for lines belonging to a specific seller."""
    return sum(
        line.total_price.gross.amount if hasattr(line, "total_price") else line.get_total().gross.amount
        for line in lines
    )


def calculate_platform_fee(
    order_total: Decimal,
    platform_fee_percentage: Decimal,
) -> Decimal:
    """Calculate platform fee from order total.

    Args:
        order_total: Total order amount (gross)
        platform_fee_percentage: Platform fee percentage (e.g., 10.00 for 10%)

    Returns:
        Platform fee amount
    """
    if order_total <= 0 or platform_fee_percentage <= 0:
        return Decimal("0.00")
    fee = (order_total * platform_fee_percentage) / Decimal("100.00")
    return fee.quantize(Decimal("0.01"))


def calculate_seller_earnings(
    order_total: Decimal,
    platform_fee: Decimal,
) -> Decimal:
    """Calculate seller earnings after platform fee deduction.

    Args:
        order_total: Total order amount (gross)
        platform_fee: Platform fee amount

    Returns:
        Seller earnings (order_total - platform_fee)
    """
    earnings = order_total - platform_fee
    return max(earnings, Decimal("0.00")).quantize(Decimal("0.01"))


def calculate_seller_order_totals(
    order_lines: list["OrderLine"],
    seller: "Seller",
    allocated_order_discount: Decimal = Decimal("0.00"),
) -> dict[str, Decimal]:
    """Calculate order totals for a specific seller from order lines.

    Args:
        order_lines: List of order lines
        seller: Seller to calculate totals for

    Returns:
        Dictionary with 'order_total', 'platform_fee', 'seller_earnings'
    """
    # Filter lines for this seller
    seller_lines = [
        line
        for line in order_lines
        if line.seller_id == seller.id
    ]

    if not seller_lines:
        return {
            "order_total": Decimal("0.00"),
            "platform_fee": Decimal("0.00"),
            "seller_earnings": Decimal("0.00"),
        }

    # Calculate total for seller's lines
    order_total = sum(
        line.total_price.gross.amount
        for line in seller_lines
        if hasattr(line, "total_price") and line.total_price
    )

    # Marketplace: allocate order-level discounts (e.g. ENTIRE_ORDER vouchers / order
    # promotions) across sellers to get a fair per-seller net total.
    if allocated_order_discount:
        order_total = max(order_total - allocated_order_discount, Decimal("0.00"))

    # Calculate platform fee
    platform_fee = calculate_platform_fee(
        order_total, seller.platform_fee_percentage
    )

    # Calculate seller earnings
    seller_earnings = calculate_seller_earnings(order_total, platform_fee)

    return {
        "order_total": order_total,
        "platform_fee": platform_fee,
        "seller_earnings": seller_earnings,
    }


def calculate_seller_revenue(
    seller: "Seller",
    start_date=None,
    end_date=None,
) -> Decimal:
    """Calculate total revenue for a seller from settlements.

    Args:
        seller: Seller instance
        start_date: Optional start date for revenue calculation
        end_date: Optional end date for revenue calculation

    Returns:
        Total revenue (order_total) as Decimal
    """
    from ..marketplace.models import SellerSettlement, SettlementStatus
    from django.utils import timezone

    settlements = SellerSettlement.objects.filter(
        seller=seller,
        status__in=[SettlementStatus.PENDING, SettlementStatus.PAID],
    )

    if start_date:
        settlements = settlements.filter(created_at__gte=start_date)
    if end_date:
        settlements = settlements.filter(created_at__lte=end_date)

    total_revenue = settlements.aggregate(
        total=models.Sum("order_total")
    )["total"] or Decimal("0.00")

    return total_revenue


def calculate_seller_earnings_total(
    seller: "Seller",
    start_date=None,
    end_date=None,
) -> Decimal:
    """Calculate total earnings for a seller (after platform fees).

    Args:
        seller: Seller instance
        start_date: Optional start date for earnings calculation
        end_date: Optional end date for earnings calculation

    Returns:
        Total seller earnings as Decimal
    """
    from ..marketplace.models import SellerSettlement, SettlementStatus

    settlements = SellerSettlement.objects.filter(
        seller=seller,
        status__in=[SettlementStatus.PENDING, SettlementStatus.PAID],
    )

    if start_date:
        settlements = settlements.filter(created_at__gte=start_date)
    if end_date:
        settlements = settlements.filter(created_at__lte=end_date)

    total_earnings = settlements.aggregate(
        total=models.Sum("seller_earnings")
    )["total"] or Decimal("0.00")

    return total_earnings


def get_seller_order_count(
    seller: "Seller",
    start_date=None,
    end_date=None,
) -> int:
    """Get count of orders for a seller.

    Args:
        seller: Seller instance
        start_date: Optional start date for order count
        end_date: Optional end date for order count

    Returns:
        Count of orders
    """
    from ..order.models import Order, OrderStatus

    orders = Order.objects.filter(
        lines__seller=seller
    ).exclude(
        status__in=[OrderStatus.DRAFT, OrderStatus.CANCELED, OrderStatus.EXPIRED]
    ).distinct()

    if start_date:
        orders = orders.filter(created_at__gte=start_date)
    if end_date:
        orders = orders.filter(created_at__lte=end_date)

    return orders.count()


def create_settlements_for_order(order: "Order") -> list["SellerSettlement"]:
    """Create settlement records for all sellers in an order.

    This function should be called when an order is paid/completed.
    It creates a settlement record for each seller that has items in the order.

    Args:
        order: Order instance to create settlements for

    Returns:
        List of created SellerSettlement instances
    """
    from ..marketplace.models import SellerSettlement, SettlementStatus

    if not order or order.is_draft():
        return []

    # Get all order lines with sellers
    order_lines = order.lines.select_related("seller").filter(seller__isnull=False)

    if not order_lines.exists():
        return []

    # Group lines by seller
    lines_by_seller = defaultdict(list)
    for line in order_lines:
        if line.seller_id:
            lines_by_seller[line.seller].append(line)

    # Compute order-level discount total (best-effort) and allocate across sellers.
    # This intentionally does NOT include line-level discounts, as those are already
    # reflected in `line.total_price`.
    allocated_discounts_by_seller: dict = {}
    try:
        from ..discount import DiscountType

        order_level_discount_total = (
            order.discounts.filter(
                type__in=[DiscountType.VOUCHER, DiscountType.PROMOTION]
            ).aggregate(total=models.Sum("amount_value"))["total"]
            or Decimal("0.00")
        )
        if order_level_discount_total and lines_by_seller:
            allocated_discounts_by_seller = allocate_discount_by_seller(
                lines_by_seller, Decimal(order_level_discount_total), "proportional"
            )
    except Exception:
        allocated_discounts_by_seller = {}

    settlements = []
    for seller, seller_lines in lines_by_seller.items():
        # Skip if seller is None or not active
        if not seller or not seller.is_active:
            continue

        # Check if settlement already exists for this seller and order
        existing_settlement = SellerSettlement.objects.filter(
            seller=seller, order=order
        ).first()
        if existing_settlement:
            continue

        # Calculate totals
        allocated_discount = allocated_discounts_by_seller.get(seller, Decimal("0.00"))
        totals = calculate_seller_order_totals(
            seller_lines, seller, allocated_order_discount=allocated_discount
        )

        if totals["order_total"] <= 0:
            continue

        # Create settlement
        settlement = SellerSettlement.objects.create(
            seller=seller,
            order=order,
            order_total=totals["order_total"],
            platform_fee=totals["platform_fee"],
            seller_earnings=totals["seller_earnings"],
            currency=order.currency,
            status=SettlementStatus.PENDING,
        )
        settlements.append(settlement)

    return settlements
