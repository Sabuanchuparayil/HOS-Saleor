from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any

import graphene
from django.db.models import Q
from prices import Money

from ...checkout.models import Checkout
from ...plugins.base_plugin import BasePlugin
from ...plugins.const import APP_ID_PREFIX
from ...product.models import ProductVariant
from ...shipping.interface import ShippingMethodData
from ...marketplace.models import (
    ProductApprovalStatus,
    ProductSubmission,
    Seller,
    SellerShippingMethod,
)


class MarketplaceShippingPlugin(BasePlugin):
    """Provide shipping methods for marketplace checkouts using SellerShippingMethod.

    This bridges marketplace shipping configuration into core Saleor checkout flow by
    emitting *external* ShippingMethodData entries. These can be selected like normal
    shipping methods and are stored on CheckoutDelivery.external_shipping_method_id.
    """

    PLUGIN_ID = "saleor.marketplace.shipping"
    PLUGIN_NAME = "Marketplace Shipping"
    PLUGIN_DESCRIPTION = "Marketplace shipping methods derived from seller configs."

    DEFAULT_ACTIVE = True
    CONFIGURATION_PER_CHANNEL = False

    @staticmethod
    def _external_id(key: str) -> str:
        # Mark as "external" for ShippingMethodData by using GraphQL type "app"
        # (see ShippingMethodData.is_external()).
        return graphene.Node.to_global_id(APP_ID_PREFIX, key)

    @staticmethod
    def _coerce_decimal(value: Any, default: Decimal = Decimal("0")) -> Decimal:
        try:
            if value is None:
                return default
            if isinstance(value, Decimal):
                return value
            return Decimal(str(value))
        except Exception:
            return default

    def _select_price_for_method(
        self,
        *,
        seller_method: SellerShippingMethod,
        seller_subtotal: Decimal,
        seller_weight: Decimal | None,
    ) -> Decimal:
        """Return seller-specific shipping price considering tiers and free threshold."""
        base = self._coerce_decimal(seller_method.price, default=Decimal("0"))

        # Free shipping threshold can be configured at SellerLogisticsConfig.
        logistics = getattr(seller_method.seller, "logistics_config", None)
        if logistics and logistics.free_shipping_threshold:
            threshold = self._coerce_decimal(logistics.free_shipping_threshold)
            if seller_subtotal >= threshold:
                return Decimal("0")

        tiers = seller_method.tiered_pricing or {}

        # Weight tiers take precedence if we have weight available.
        if seller_weight is not None:
            for tier in tiers.get("weight_tiers", []) or []:
                min_w = self._coerce_decimal(tier.get("min_weight"), default=Decimal("0"))
                if seller_weight >= min_w:
                    return self._coerce_decimal(tier.get("price"), default=base)

        # Otherwise try price tiers based on subtotal.
        for tier in tiers.get("price_tiers", []) or []:
            min_p = self._coerce_decimal(tier.get("min_price"), default=Decimal("0"))
            if seller_subtotal >= min_p:
                return self._coerce_decimal(tier.get("price"), default=base)

        return base

    def _apply_seller_type_adjustments(
        self,
        *,
        seller_method: SellerShippingMethod,
        base_price: Decimal,
    ) -> Decimal:
        """Apply seller-type specific adjustments (e.g. B2B negotiated discount factor)."""
        seller = seller_method.seller
        if getattr(seller, "seller_type", None) != "b2b_wholesale":
            return base_price

        logistics = getattr(seller, "logistics_config", None)
        if not logistics:
            return base_price

        # Matches existing utility logic: logistics_config.custom_shipping_methods["b2b_discount_factor"]
        try:
            factor_raw = (logistics.custom_shipping_methods or {}).get(
                "b2b_discount_factor"
            )
            if factor_raw is None:
                return base_price
            factor = self._coerce_decimal(factor_raw, default=Decimal("1"))
            return (base_price * factor).quantize(Decimal("0.01"))
        except Exception:
            return base_price

    def get_shipping_methods_for_checkout(
        self,
        checkout: Checkout,
        built_in_shipping_methods: list[ShippingMethodData],
        previous_value: Any,
    ) -> list[ShippingMethodData]:
        # If checkout doesn't require shipping or has no address yet, do nothing.
        if not checkout.is_shipping_required():
            return []
        if not checkout.shipping_address:
            return []

        country_code = checkout.shipping_address.country.code
        city = (checkout.shipping_address.city or "").strip() or None

        # Load checkout lines + variants + products with minimal queries.
        lines = checkout.lines.select_related("variant", "variant__product").all()
        if not lines:
            return []

        product_ids = {line.variant.product_id for line in lines}

        # Resolve seller ownership via ProductSubmission (approved).
        submissions = (
            ProductSubmission.objects.filter(
                product_id__in=product_ids,
                status=ProductApprovalStatus.APPROVED,
            )
            .select_related("seller")
            .order_by("product_id", "-submitted_at")
        )

        product_to_seller: dict[int, Seller] = {}
        for sub in submissions:
            # keep latest per product
            product_to_seller.setdefault(sub.product_id, sub.seller)

        if not product_to_seller:
            return []

        # Compute per-seller subtotal/weight for tier rules.
        subtotal_by_seller: dict[Seller, Decimal] = defaultdict(lambda: Decimal("0"))
        weight_by_seller: dict[Seller, Decimal] = defaultdict(lambda: Decimal("0"))

        for line in lines:
            seller = product_to_seller.get(line.variant.product_id)
            if not seller:
                continue
            # Prefer stored line totals if present; fallback to undiscounted unit price.
            unit = self._coerce_decimal(line.undiscounted_unit_price_amount, default=Decimal("0"))
            line_total = unit * Decimal(line.quantity)
            subtotal_by_seller[seller] += line_total

            try:
                variant: ProductVariant = line.variant
                if variant.weight:
                    # measurement.measures.Weight exposes "kg" for Weight.
                    weight_by_seller[seller] += self._coerce_decimal(
                        getattr(variant.weight, "kg", None)
                    )
            except Exception:
                pass

        sellers = list({s for s in product_to_seller.values() if s})
        if not sellers:
            return []

        # Fetch active seller methods applicable to destination.
        q = Q(destination_country__isnull=True) | Q(destination_country=country_code)
        if city:
            q &= Q(destination_city__isnull=True) | Q(destination_city__iexact=city)
        else:
            q &= Q(destination_city__isnull=True)

        seller_methods = (
            SellerShippingMethod.objects.filter(seller__in=sellers, is_active=True)
            .filter(q)
            .select_related("seller")
            .order_by("seller_id", "name")
        )

        methods_by_seller: dict[Seller, list[SellerShippingMethod]] = defaultdict(list)
        for m in seller_methods:
            methods_by_seller[m.seller].append(m)

        if not methods_by_seller:
            return []

        # Determine the set of method names offered across sellers.
        names: set[str] = set()
        for ms in methods_by_seller.values():
            names.update([m.name for m in ms if m.name])

        # Compute each seller's "fallback" method (cheapest after seller logic).
        fallback_by_seller: dict[Seller, SellerShippingMethod] = {}
        for seller, ms in methods_by_seller.items():
            best: tuple[Decimal, SellerShippingMethod] | None = None
            for m in ms:
                base = self._select_price_for_method(
                    seller_method=m,
                    seller_subtotal=subtotal_by_seller.get(seller, Decimal("0")),
                    seller_weight=weight_by_seller.get(seller),
                )
                price = self._apply_seller_type_adjustments(
                    seller_method=m, base_price=base
                )
                if best is None or price < best[0]:
                    best = (price, m)
            if best is not None:
                fallback_by_seller[seller] = best[1]

        # Build external ShippingMethodData, aggregating per-seller prices.
        results: list[ShippingMethodData] = []
        for name in sorted(names):
            total = Decimal("0")
            min_days: int | None = None
            max_days: int | None = None

            for seller in sellers:
                seller_methods = methods_by_seller.get(seller) or []
                picked = next((m for m in seller_methods if m.name == name), None)
                if picked is None:
                    picked = fallback_by_seller.get(seller)
                if picked is None:
                    continue

                base = self._select_price_for_method(
                    seller_method=picked,
                    seller_subtotal=subtotal_by_seller.get(seller, Decimal("0")),
                    seller_weight=weight_by_seller.get(seller),
                )
                price = self._apply_seller_type_adjustments(
                    seller_method=picked, base_price=base
                )
                total += price

                if picked.estimated_days is not None:
                    min_days = (
                        picked.estimated_days
                        if min_days is None
                        else min(min_days, picked.estimated_days)
                    )
                    max_days = (
                        picked.estimated_days
                        if max_days is None
                        else max(max_days, picked.estimated_days)
                    )

            # If no sellers contributed, don't emit this method.
            if total < Decimal("0"):  # pragma: no cover (defensive)
                continue

            key = f"marketplace-shipping:{checkout.channel_id}:{name}"
            results.append(
                ShippingMethodData(
                    id=self._external_id(key),
                    name=name,
                    description="Marketplace shipping (aggregated per seller)",
                    price=Money(total.quantize(Decimal("0.01")), checkout.currency),
                    minimum_delivery_days=min_days,
                    maximum_delivery_days=max_days,
                    metadata={"source": "marketplace", "method": name},
                )
            )

        return results


