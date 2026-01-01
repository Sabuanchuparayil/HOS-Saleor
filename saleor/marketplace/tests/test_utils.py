"""Tests for marketplace utility functions."""

from decimal import Decimal

import pytest
from prices import Money, TaxedMoney

from ...order.models import OrderLine
from ...product.models import Product
from ..utils import (
    allocate_discount_by_seller,
    allocate_shipping_cost_by_seller,
    calculate_seller_subtotal,
    group_lines_by_seller,
)


@pytest.fixture
def order_lines_with_sellers(db, seller, product):
    """Create order lines with different sellers."""
    from ...order.models import Order
    from ...product.models import ProductVariant

    order = Order.objects.create(
        currency="USD",
        total_net_amount=Decimal("100.00"),
        total_gross_amount=Decimal("120.00"),
    )

    # Create product variant
    variant = ProductVariant.objects.create(
        product=product,
        sku="TEST-SKU-1",
    )

    # Create order lines
    line1 = OrderLine.objects.create(
        order=order,
        product=product,
        variant=variant,
        product_name="Product 1",
        variant_name="Variant 1",
        quantity=1,
        unit_price_net_amount=Decimal("50.00"),
        unit_price_gross_amount=Decimal("60.00"),
        total_price_net_amount=Decimal("50.00"),
        total_price_gross_amount=Decimal("60.00"),
        seller=seller,
        seller_name=seller.store_name,
    )

    # Create another seller and product
    from ...account.models import User
    from ...channel.models import Channel
    from ..models import Seller, SellerStatus

    seller2 = Seller.objects.create(
        store_name="Seller 2",
        slug="seller-2",
        owner=User.objects.create_user(email="seller2@example.com"),
        channel=Channel.objects.first(),
        status=SellerStatus.ACTIVE,
    )
    product2 = Product.objects.create(
        name="Product 2",
        slug="product-2",
        product_type=product.product_type,
    )
    variant2 = ProductVariant.objects.create(
        product=product2,
        sku="TEST-SKU-2",
    )
    product2.seller = seller2
    product2.save()

    line2 = OrderLine.objects.create(
        order=order,
        product=product2,
        variant=variant2,
        product_name="Product 2",
        variant_name="Variant 2",
        quantity=1,
        unit_price_net_amount=Decimal("50.00"),
        unit_price_gross_amount=Decimal("60.00"),
        total_price_net_amount=Decimal("50.00"),
        total_price_gross_amount=Decimal("60.00"),
        seller=seller2,
        seller_name=seller2.store_name,
    )

    return [line1, line2]


def test_group_lines_by_seller(order_lines_with_sellers):
    """Test grouping order lines by seller."""
    grouped = group_lines_by_seller(order_lines_with_sellers)
    
    assert len(grouped) == 2
    assert all(isinstance(seller, type(order_lines_with_sellers[0].seller)) or seller is None for seller in grouped.keys())


def test_allocate_shipping_cost_by_seller_equal(order_lines_with_sellers):
    """Test equal shipping cost allocation."""
    lines_by_seller = group_lines_by_seller(order_lines_with_sellers)
    total_shipping = Decimal("10.00")
    
    allocation = allocate_shipping_cost_by_seller(
        lines_by_seller, total_shipping, "equal"
    )
    
    assert len(allocation) == 2
    # Each seller should get half
    assert allocation[order_lines_with_sellers[0].seller] == Decimal("5.00")
    assert allocation[order_lines_with_sellers[1].seller] == Decimal("5.00")


def test_allocate_shipping_cost_by_seller_proportional(order_lines_with_sellers):
    """Test proportional shipping cost allocation."""
    lines_by_seller = group_lines_by_seller(order_lines_with_sellers)
    total_shipping = Decimal("10.00")
    
    allocation = allocate_shipping_cost_by_seller(
        lines_by_seller, total_shipping, "proportional"
    )
    
    assert len(allocation) == 2
    # Both have same value, so should be equal
    total_allocated = sum(allocation.values())
    assert total_allocated == total_shipping


def test_allocate_discount_by_seller(order_lines_with_sellers):
    """Test discount allocation by seller."""
    lines_by_seller = group_lines_by_seller(order_lines_with_sellers)
    total_discount = Decimal("5.00")
    
    allocation = allocate_discount_by_seller(
        lines_by_seller, total_discount, "proportional"
    )
    
    assert len(allocation) == 2
    total_allocated = sum(allocation.values())
    assert total_allocated == total_discount


def test_calculate_seller_subtotal(order_lines_with_sellers, seller):
    """Test calculating subtotal for a seller."""
    seller_lines = [line for line in order_lines_with_sellers if line.seller == seller]
    subtotal = calculate_seller_subtotal(seller_lines)
    
    assert subtotal > 0
    assert isinstance(subtotal, Decimal)
