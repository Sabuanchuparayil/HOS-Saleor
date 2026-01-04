from decimal import Decimal

import pytest

from saleor.checkout.fetch import fetch_checkout_info, fetch_checkout_lines, fetch_shipping_methods_for_checkout
from saleor.marketplace.models import (
    ProductApprovalStatus,
    ProductSubmission,
    Seller,
    SellerLogisticsConfig,
    SellerShippingMethod,
)
from saleor.plugins.manager import get_plugins_manager


@pytest.mark.django_db
def test_marketplace_shipping_plugin_emits_external_methods_for_checkout(
    settings,
    checkout_with_items_and_shipping,
    staff_user,
):
    # given
    settings.PLUGINS = [
        "saleor.plugins.marketplace_shipping.plugin.MarketplaceShippingPlugin",
    ]
    manager = get_plugins_manager(allow_replica=False)

    checkout = checkout_with_items_and_shipping
    lines, _ = fetch_checkout_lines(checkout)

    seller = Seller.objects.create(
        store_name="Demo Seller",
        slug="demo-seller",
        owner=staff_user,
        status="active",
        seller_type="b2c_retail",
    )
    SellerLogisticsConfig.objects.create(seller=seller)

    SellerShippingMethod.objects.create(
        seller=seller,
        name="Standard Shipping",
        price=Decimal("9.99"),
        is_active=True,
        destination_country=checkout.shipping_address.country.code,
        estimated_days=5,
    )

    # Link checkout products to seller via approved submissions
    for line in checkout.lines.select_related("variant", "variant__product"):
        ProductSubmission.objects.create(
            seller=seller,
            product=line.variant.product,
            status=ProductApprovalStatus.APPROVED,
        )

    checkout_info = fetch_checkout_info(checkout, lines, manager)

    # when
    deliveries = fetch_shipping_methods_for_checkout(checkout_info)

    # then
    assert deliveries, "Expected marketplace shipping methods to be available"
    assert any(d.is_external for d in deliveries)
    assert any((d.name or "").lower() == "standard shipping" for d in deliveries)
    std = next(d for d in deliveries if (d.name or "").lower() == "standard shipping")
    assert std.currency == checkout.currency
    assert std.price_amount == Decimal("9.99")


