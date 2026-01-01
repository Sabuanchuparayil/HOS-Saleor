"""Seller-aware tax calculation plugin for marketplace."""

from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from django.conf import settings

from ...plugins.base_plugin import BasePlugin
from ...plugins.models import PluginConfiguration
from ...tax.utils import get_charge_taxes_for_checkout, get_charge_taxes_for_order
from ..models import Seller, SellerTaxRegistration

if TYPE_CHECKING:
    from ...account.models import Address
    from ...checkout.fetch import CheckoutInfo, CheckoutLineInfo
    from ...order.fetch import OrderLineInfo
    from ...order.models import Order, OrderLine
    from ...product.models import Product, ProductVariant
    from prices import Money, TaxedMoney
    from ...order.interface import OrderTaxedPricesData


class SellerAwareTaxPlugin(BasePlugin):
    """Plugin for seller-aware tax calculations in marketplace.

    This plugin calculates taxes based on seller-specific tax registrations
    and tax origin addresses, enabling multi-vendor marketplace tax compliance.
    """

    PLUGIN_ID = "saleor.marketplace.plugins.seller_aware_tax"
    PLUGIN_NAME = "Seller-Aware Tax"
    DEFAULT_ACTIVE = True
    DEFAULT_CONFIGURATION = [
        {"name": "Use seller tax origin", "value": True},
        {"name": "Fallback to channel tax configuration", "value": True},
    ]

    CONFIG_STRUCTURE = {
        "Use seller tax origin": {
            "type": "boolean",
            "help_text": (
                "When enabled, uses seller's tax origin address for tax calculations. "
                "When disabled, uses channel/site default tax configuration."
            ),
            "label": "Use seller tax origin",
        },
        "Fallback to channel tax configuration": {
            "type": "boolean",
            "help_text": (
                "When enabled and seller has no tax registration, "
                "falls back to channel tax configuration."
            ),
            "label": "Fallback to channel tax configuration",
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = self._get_plugin_configuration()

    def _get_plugin_configuration(self) -> PluginConfiguration:
        """Get or create plugin configuration."""
        configuration, _ = PluginConfiguration.objects.get_or_create(
            identifier=self.PLUGIN_ID,
            defaults={
                "name": self.PLUGIN_NAME,
                "active": self.DEFAULT_ACTIVE,
                "configuration": self.DEFAULT_CONFIGURATION,
            },
        )
        return configuration

    def _get_seller_tax_registration(
        self, seller, country_code: str, tax_type: str = "vat"
    ) -> Optional[SellerTaxRegistration]:
        """Get seller's tax registration for a specific country and type.
        
        Args:
            seller: The seller instance
            country_code: Country code (e.g., "US", "GB")
            tax_type: Tax registration type, one of "vat", "gst", "sales_tax", "other"
        
        Returns:
            SellerTaxRegistration instance or None
        """
        if not seller:
            return None

        try:
            return SellerTaxRegistration.objects.filter(
                seller=seller, 
                country=country_code, 
                registration_type=tax_type.lower(),
                is_active=True
            ).first()
        except Exception:
            return None

    def _get_seller_for_product(self, product) -> Optional["Seller"]:
        """Get seller associated with a product."""
        if not product:
            return None
        return getattr(product, "seller", None)

    def _get_seller_for_order_line(self, order_line) -> Optional["Seller"]:
        """Get seller associated with an order line (denormalized)."""
        if not order_line:
            return None
        # First check denormalized seller field
        seller = getattr(order_line, "seller", None)
        if seller:
            return seller
        # Fallback to product seller
        if hasattr(order_line, "variant") and order_line.variant:
            product = getattr(order_line.variant, "product", None)
            if product:
                return self._get_seller_for_product(product)
        return None

    def calculate_checkout_line_unit_price(
        self,
        checkout_info: "CheckoutInfo",
        lines: list["CheckoutLineInfo"],
        checkout_line_info: "CheckoutLineInfo",
        address: Optional["Address"],
        previous_value: "TaxedMoney",
    ) -> "TaxedMoney":
        """Calculate checkout line unit price with seller-aware tax."""
        # Get configuration
        use_seller_tax_origin = self._get_config_value("Use seller tax origin", True)
        if not use_seller_tax_origin:
            return previous_value

        # Check if taxes should be charged
        if not get_charge_taxes_for_checkout(checkout_info):
            return previous_value

        # Get seller from product
        product = checkout_line_info.product
        seller = self._get_seller_for_product(product)

        if not seller:
            return previous_value

        # Determine which country to use for tax calculation
        # For origin-based tax systems, use seller's tax origin address
        # For destination-based tax systems, use shipping address country
        country_code = None
        
        # Check if seller has tax origin address (for origin-based taxation)
        if hasattr(seller, "tax_origin_address") and seller.tax_origin_address:
            origin_country = seller.tax_origin_address.country
            if origin_country:
                # Use seller's tax origin country for origin-based tax calculation
                country_code = origin_country.code
        
        # Fallback to destination country (shipping address)
        if not country_code:
            country_code = address.country.code if address and address.country else None
        
        if not country_code:
            return previous_value

        # Get seller tax registration for the determined country
        tax_registration = self._get_seller_tax_registration(
            seller, country_code, "vat"
        )

        # If no tax registration and fallback is enabled, use previous value
        fallback_enabled = self._get_config_value(
            "Fallback to channel tax configuration", True
        )
        if not tax_registration and fallback_enabled:
            return previous_value

        # Get tax rate from TaxClassCountryRate based on country and product tax class
        from ...tax.models import TaxClassCountryRate
        from django.conf import settings
        
        # Get product tax class if available
        tax_class = getattr(product, "tax_class", None)
        if not tax_class and hasattr(product, "product_type"):
            tax_class = getattr(product.product_type, "tax_class", None)
        
        # Look up tax rate from TaxClassCountryRate
        # Use default connection for tax rate lookup
        database_connection_name = settings.DATABASE_CONNECTION_DEFAULT_NAME
        
        tax_rate_obj = None
        if tax_class:
            # Use tax class specific rate
            tax_rate_obj = TaxClassCountryRate.objects.using(database_connection_name).filter(
                tax_class=tax_class,
                country=country_code
            ).first()
        
        if not tax_rate_obj:
            # Fall back to default country rate (tax_class=None)
            tax_rate_obj = TaxClassCountryRate.objects.using(database_connection_name).filter(
                country=country_code,
                tax_class=None
            ).first()
        
        # If we found a tax rate, apply it
        if tax_rate_obj:
            from ...tax.calculations import calculate_flat_rate_tax
            from prices import Money
            
            # Check if prices are entered with tax
            channel = checkout_info.channel
            prices_entered_with_tax = (
                channel.tax_configuration.prices_entered_with_tax
                if hasattr(channel, "tax_configuration") and channel.tax_configuration
                else True
            )
            
            # Calculate taxed price using the tax rate
            tax_rate = tax_rate_obj.rate
            net_amount = Money(previous_value.net.amount, previous_value.currency)
            
            return calculate_flat_rate_tax(
                net_amount, tax_rate, prices_entered_with_tax
            )

        # Fallback to previous value if no tax rate found
        return previous_value

    def calculate_order_line_unit(
        self,
        order: "Order",
        order_line: "OrderLine",
        variant: "ProductVariant",
        product: "Product",
        previous_value: "OrderTaxedPricesData",
    ) -> "OrderTaxedPricesData":
        """Calculate order line unit price with seller-aware tax."""
        # Get configuration
        use_seller_tax_origin = self._get_config_value("Use seller tax origin", True)
        if not use_seller_tax_origin:
            return previous_value

        # Check if taxes should be charged
        if not get_charge_taxes_for_order(order):
            return previous_value

        # Get seller from order line (denormalized) or product
        seller = self._get_seller_for_order_line(order_line)
        if not seller:
            seller = self._get_seller_for_product(product)

        if not seller:
            return previous_value

        # Determine which country to use for tax calculation
        # For origin-based tax systems, use seller's tax origin address
        # For destination-based tax systems, use shipping address country
        country_code = None
        
        # Check if seller has tax origin address (for origin-based taxation)
        if hasattr(seller, "tax_origin_address") and seller.tax_origin_address:
            origin_country = seller.tax_origin_address.country
            if origin_country:
                # Use seller's tax origin country for origin-based tax calculation
                country_code = origin_country.code
        
        # Fallback to destination country (shipping address)
        if not country_code:
            shipping_address = order.shipping_address
            country_code = (
                shipping_address.country.code
                if shipping_address and shipping_address.country
                else None
            )
        
        if not country_code:
            return previous_value

        # Get seller tax registration for the determined country
        tax_registration = self._get_seller_tax_registration(
            seller, country_code, "vat"
        )

        # If no tax registration and fallback is enabled, use previous value
        fallback_enabled = self._get_config_value(
            "Fallback to channel tax configuration", True
        )
        if not tax_registration and fallback_enabled:
            return previous_value

        # Get tax rate from TaxClassCountryRate based on country and product tax class
        from ...tax.models import TaxClassCountryRate, TaxClass
        
        # Get product tax class from order line or product
        tax_class = None
        if hasattr(order_line, "tax_class_id") and order_line.tax_class_id:
            try:
                tax_class = TaxClass.objects.get(id=order_line.tax_class_id)
            except TaxClass.DoesNotExist:
                pass
        
        if not tax_class:
            tax_class = getattr(product, "tax_class", None)
        if not tax_class and hasattr(product, "product_type"):
            tax_class = getattr(product.product_type, "tax_class", None)
        
        # Look up tax rate from TaxClassCountryRate
        database_connection_name = settings.DATABASE_CONNECTION_DEFAULT_NAME
        
        tax_rate_obj = None
        if tax_class:
            # Use tax class specific rate
            tax_rate_obj = TaxClassCountryRate.objects.using(database_connection_name).filter(
                tax_class=tax_class,
                country=country_code
            ).first()
        
        if not tax_rate_obj:
            # Fall back to default country rate (tax_class=None)
            tax_rate_obj = TaxClassCountryRate.objects.using(database_connection_name).filter(
                country=country_code,
                tax_class=None
            ).first()
        
        # If we found a tax rate, apply it
        if tax_rate_obj:
            from ...tax.calculations import calculate_flat_rate_tax
            from prices import Money
            
            tax_rate = tax_rate_obj.rate
            currency = order.currency
            
            # Get prices_entered_with_tax from order or channel
            prices_entered_with_tax = getattr(order, "prices_entered_with_tax", True)
            if not hasattr(order, "prices_entered_with_tax") and hasattr(order, "channel"):
                channel = order.channel
                if hasattr(channel, "tax_configuration") and channel.tax_configuration:
                    prices_entered_with_tax = channel.tax_configuration.prices_entered_with_tax
            
            # Get undiscounted and discounted prices
            undiscounted_price = previous_value.undiscounted_price
            price_with_discounts = previous_value.price_with_discounts
            
            # Calculate taxed prices using the tax calculation function
            undiscounted_net = Money(undiscounted_price.net.amount, currency)
            undiscounted_taxed = calculate_flat_rate_tax(
                undiscounted_net, tax_rate, prices_entered_with_tax
            )
            
            discounted_net = Money(price_with_discounts.net.amount, currency)
            discounted_taxed = calculate_flat_rate_tax(
                discounted_net, tax_rate, prices_entered_with_tax
            )
            
            return OrderTaxedPricesData(
                undiscounted_price=undiscounted_taxed,
                price_with_discounts=discounted_taxed,
            )
        
        # Fallback: use default tax calculation
        # This will use channel/site tax configuration or tax class
        return previous_value

    def _get_config_value(self, field_name: str, default_value):
        """Get configuration value for a field."""
        if not self.config or not self.config.configuration:
            return default_value

        for item in self.config.configuration:
            if item.get("name") == field_name:
                return item.get("value", default_value)
        return default_value
