"""Discount configuration models for marketplace."""

from decimal import Decimal
from uuid import uuid4

from django.contrib.postgres.indexes import BTreeIndex
from django.core.validators import MinValueValidator
from django.db import models

from ..core.models import ModelWithMetadata


class SellerDiscountConfig(ModelWithMetadata):
    """Seller-specific discount configuration and rules."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    seller = models.OneToOneField(
        "marketplace.Seller",
        related_name="discount_config",
        on_delete=models.CASCADE,
        help_text="Seller this discount configuration belongs to",
    )
    max_discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Maximum discount percentage this seller can offer (e.g., 50.00 for 50%)",
    )
    min_order_value_for_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Minimum order value required to apply discounts",
    )
    allow_sku_level_discounts = models.BooleanField(
        default=True,
        help_text="Whether seller can create SKU-level discounts",
    )
    allow_category_level_discounts = models.BooleanField(
        default=True,
        help_text="Whether seller can create category-level discounts",
    )
    allow_seller_level_discounts = models.BooleanField(
        default=True,
        help_text="Whether seller can create seller-wide discounts",
    )
    discount_rules = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional discount rules and configuration (JSON)",
    )

    class Meta:
        ordering = ("seller",)
        indexes = [
            BTreeIndex(fields=["seller"], name="discount_config_seller_idx"),
        ]

    def __str__(self):
        return f"Discount config for {self.seller.store_name}"

