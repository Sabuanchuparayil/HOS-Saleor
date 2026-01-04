"""GraphQL types for marketplace."""

import graphene
from graphene import relay

from saleor.marketplace import models
from ..core.connection import CountableConnection
from ..core.doc_category import DOC_CATEGORY_MARKETPLACE
from ..core.fields import BaseField, ConnectionField, JSONString
from ..core.scalars import DateTime, Decimal
from ..core.types import CountryDisplay, Image, ModelObjectType, Money
from .enums import (
    DistributorCategoryEnum,
    FulfillmentMethodEnum,
    ProductApprovalStatusEnum,
    ReturnRequestStatusEnum,
    SellerDomainStatusEnum,
    SellerStatusEnum,
    SellerTypeEnum,
    SettlementStatusEnum,
    PricingTypeEnum,
)


class Seller(ModelObjectType[models.Seller]):
    """Represents a seller/vendor in the marketplace."""

    class Meta:
        description = "Represents a seller/vendor in the marketplace."
        model = models.Seller
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    store_name = graphene.String(required=True)
    slug = graphene.String(required=True)
    description = graphene.String()
    logo = graphene.Field(Image)
    status = SellerStatusEnum(required=True)
    seller_type = SellerTypeEnum(required=True)
    is_authorized_distributor = graphene.Boolean(required=True)
    distributor_category = DistributorCategoryEnum()
    minimum_order_quantity = graphene.Int()
    credit_terms_enabled = graphene.Boolean(required=True)
    business_registration_number = graphene.String()
    platform_fee_percentage = Decimal(required=True)
    stripe_account_id = graphene.String()
    tax_origin_address = graphene.Field("saleor.graphql.account.types.Address")
    channel = graphene.Field("saleor.graphql.channel.types.Channel")
    logistics_config = graphene.Field("saleor.graphql.marketplace.types.SellerLogisticsConfig")
    discount_config = graphene.Field(
        "saleor.graphql.marketplace.types.SellerDiscountConfig",
        description="Seller-specific discount configuration (marketplace).",
    )
    created_at = DateTime(required=True)
    updated_at = DateTime(required=True)

    analytics = graphene.Field(
        "saleor.graphql.marketplace.types.SellerAnalytics",
        period=graphene.Argument("saleor.graphql.core.enums.ReportingPeriod"),
        seller_type=graphene.Argument(
            "saleor.graphql.marketplace.enums.SellerTypeEnum",
            description="Filter analytics by seller type (B2B, B2C, Hybrid). Only returns data if seller matches type.",
        ),
        description="Analytics data for this seller.",
    )
    products = ConnectionField(
        "saleor.graphql.product.types.products.ProductCountableConnection",
        channel=graphene.Argument(
            graphene.String,
            description="Slug of a channel for which the data should be returned."
        ),
        description="List of products for this seller.",
    )
    orders = ConnectionField(
        "saleor.graphql.order.types.OrderCountableConnection",
        description="List of orders for this seller.",
    )
    settlements = ConnectionField(
        "saleor.graphql.marketplace.types.SellerSettlementCountableConnection",
        description="List of settlements/payouts for this seller.",
    )

    @staticmethod
    def resolve_channel(root: models.Seller, info):
        return root.channel

    @staticmethod
    def resolve_products(root: models.Seller, info, channel=None, **kwargs):
        """Resolve products for this seller."""
        from ...product import models as product_models
        from ..core.connection import create_connection_slice
        from ...core.context import ChannelContext
        from ..core.context import get_database_connection_name
        from ..product.types.products import ProductCountableConnection
        
        connection_name = get_database_connection_name(info.context)
        qs = product_models.Product.objects.using(connection_name).filter(seller=root)
        
        channel_obj = None
        # Apply channel filtering if provided
        if channel:
            from ...channel.models import Channel as ChannelModel
            try:
                channel_obj = ChannelModel.objects.using(connection_name).get(slug=channel)
                # Filter by channel listing
                published_products = product_models.ProductChannelListing.objects.using(
                    connection_name
                ).filter(
                    channel=channel_obj,
                    is_published=True,
                ).values_list("product_id", flat=True)
                qs = qs.filter(id__in=published_products)
            except ChannelModel.DoesNotExist:
                qs = product_models.Product.objects.none()
        
        # Apply visibility filtering:
        # - seller owner/staff can see all their products (including pending)
        # - others see only storefront-visible products
        from ..utils import get_user_or_app_from_context
        requestor = get_user_or_app_from_context(info.context)
        if requestor and hasattr(requestor, "pk"):
            is_seller_staff = (
                root.owner_id == requestor.pk
                or root.staff.filter(pk=requestor.pk).exists()
            )
        else:
            is_seller_staff = False
        if not is_seller_staff:
            # visible_to_user expects a Channel object (or None), not a slug string.
            qs = qs.visible_to_user(
                requestor,
                channel_obj,
                limited_channel_access=bool(channel),
            )
        
        # Wrap in ChannelContext
        channel_contexts = [
            ChannelContext(node=product, channel_slug=channel)
            for product in qs
        ]
        
        return create_connection_slice(
            channel_contexts, info, kwargs, ProductCountableConnection
        )

    @staticmethod
    def resolve_orders(root: models.Seller, info, **kwargs):
        """Resolve orders for this seller."""
        from ...order import models as order_models
        from ..core.connection import create_connection_slice
        from ..core.context import get_database_connection_name
        from ..order.types import OrderCountableConnection
        
        connection_name = get_database_connection_name(info.context)
        # Filter orders that have at least one order line belonging to this seller
        qs = order_models.Order.objects.using(connection_name).filter(
            lines__seller=root
        ).distinct()
        
        return create_connection_slice(qs, info, kwargs, OrderCountableConnection)

    @staticmethod
    def resolve_settlements(root: models.Seller, info, **kwargs):
        """Resolve settlements for this seller."""
        from ..core.connection import create_connection_slice
        from ..core.context import get_database_connection_name
        
        connection_name = get_database_connection_name(info.context)
        qs = models.SellerSettlement.objects.using(connection_name).filter(seller=root)
        
        # SellerSettlementCountableConnection is defined later in this file
        # Use string reference to avoid forward reference issues
        from ..core.connection import create_connection_slice as _create_slice
        # Import the connection class by name from this module at runtime
        import sys
        this_module = sys.modules[__name__]
        SettlementConnection = getattr(this_module, 'SellerSettlementCountableConnection')
        
        return _create_slice(qs, info, kwargs, SettlementConnection)

    @staticmethod
    def resolve_logistics_config(root: models.Seller, info):
        """Resolve logistics configuration for this seller."""
        try:
            return root.logistics_config
        except models.SellerLogisticsConfig.DoesNotExist:
            return None

    @staticmethod
    def resolve_discount_config(root: models.Seller, info):
        """Resolve discount configuration for this seller."""
        try:
            return root.discount_config
        except Exception:
            return None

    @staticmethod
    def resolve_analytics(root: models.Seller, info, period=None, seller_type=None):
        from saleor.marketplace.utils import (
            calculate_seller_earnings_total,
            calculate_seller_revenue,
            get_seller_order_count,
        )
        from ..utils.filters import reporting_period_to_date
        from ...core.prices import Money
        from decimal import Decimal

        # If seller_type filter is provided, filter analytics by seller type
        # This allows separating B2B vs B2C analytics
        if seller_type:
            seller_type_value = seller_type.value if hasattr(seller_type, 'value') else seller_type
            # If seller_type doesn't match, return zero analytics
            if root.seller_type != seller_type_value:
                currency = root.channel.currency_code if root.channel else "USD"
                return SellerAnalytics(
                    revenue=Money(Decimal("0"), currency),
                    earnings=Money(Decimal("0"), currency),
                    order_count=0,
                    platform_fee_total=Money(Decimal("0"), currency),
                )

        start_date = None
        if period:
            start_date = reporting_period_to_date(period)

        revenue = calculate_seller_revenue(root, start_date=start_date)
        earnings = calculate_seller_earnings_total(root, start_date=start_date)
        order_count = get_seller_order_count(root, start_date=start_date)

        # Calculate platform fee total
        platform_fee_total = revenue - earnings

        # Get default currency from seller's first settlement or channel
        currency = "USD"  # Default
        if hasattr(root, "settlements") and root.settlements.exists():
            currency = root.settlements.first().currency
        elif root.channel and hasattr(root.channel, "currency_code"):
            currency = root.channel.currency_code

        return SellerAnalytics(
            revenue=Money(revenue, currency),
            earnings=Money(earnings, currency),
            order_count=order_count,
            platform_fee_total=Money(platform_fee_total, currency),
        )


class SellerDiscountConfig(ModelObjectType[models.SellerDiscountConfig]):
    """Seller-specific discount configuration."""

    class Meta:
        description = "Seller-specific discount configuration (marketplace)."
        model = models.SellerDiscountConfig
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    max_discount_percentage = Decimal()
    min_order_value_for_discount = Decimal()
    allow_sku_level_discounts = graphene.Boolean(required=True)
    allow_category_level_discounts = graphene.Boolean(required=True)
    allow_seller_level_discounts = graphene.Boolean(required=True)
    discount_rules = JSONString()
    created_at = DateTime(required=True)
    updated_at = DateTime(required=True)


class SellerAnalytics(graphene.ObjectType):
    """Analytics data for a seller."""

    class Meta:
        description = "Analytics data for a seller including revenue, earnings, and order counts."
        doc_category = DOC_CATEGORY_MARKETPLACE

    revenue = graphene.Field(Money, description="Total revenue (order total) for the seller.")
    earnings = graphene.Field(
        Money, description="Total earnings (after platform fees) for the seller."
    )
    order_count = graphene.Int(description="Total number of orders for the seller.")
    platform_fee_total = graphene.Field(
        Money, description="Total platform fees collected from the seller."
    )


class SellerSettlement(ModelObjectType[models.SellerSettlement]):
    """Represents a settlement/payout for a seller."""

    class Meta:
        description = "Represents a settlement/payout record for a seller from an order."
        model = models.SellerSettlement
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    seller = graphene.Field("saleor.graphql.marketplace.types.Seller", required=True)
    order = graphene.Field("saleor.graphql.order.types.Order")
    order_total = graphene.Field(Money, required=True)
    platform_fee = graphene.Field(Money, required=True)
    seller_earnings = graphene.Field(Money, required=True)
    currency = graphene.String(required=True)
    status = graphene.Field("saleor.graphql.marketplace.enums.SettlementStatusEnum", required=True)
    stripe_transfer_id = graphene.String()
    payout_reference = graphene.String()
    notes = graphene.String()
    created_at = DateTime(required=True)
    updated_at = DateTime(required=True)
    paid_at = DateTime()

    @staticmethod
    def resolve_order_total(root: models.SellerSettlement, info):
        from ...core.prices import Money

        return Money(root.order_total, root.currency)

    @staticmethod
    def resolve_platform_fee(root: models.SellerSettlement, info):
        from ...core.prices import Money

        return Money(root.platform_fee, root.currency)

    @staticmethod
    def resolve_seller_earnings(root: models.SellerSettlement, info):
        from ...core.prices import Money

        return Money(root.seller_earnings, root.currency)


class SellerSettlementCountableConnection(CountableConnection):
    """Connection type for SellerSettlement list queries."""

    class Meta:
        node = SellerSettlement
        doc_category = DOC_CATEGORY_MARKETPLACE


class SellerDomain(ModelObjectType[models.SellerDomain]):
    """Represents a domain/subdomain for a seller's storefront."""

    class Meta:
        description = "Represents a domain or subdomain for a seller's storefront."
        model = models.SellerDomain
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    domain = graphene.String(required=True)
    is_primary = graphene.Boolean(required=True)
    status = SellerDomainStatusEnum(required=True)
    ssl_enabled = graphene.Boolean(required=True)
    verified_at = DateTime()
    created_at = DateTime(required=True)
    updated_at = DateTime(required=True)


class Theme(ModelObjectType[models.Theme]):
    """Theme template definition for storefront customization."""

    class Meta:
        description = "Theme template definition for storefront customization."
        model = models.Theme
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    slug = graphene.String(required=True)
    description = graphene.String()
    is_default = graphene.Boolean(required=True)
    is_active = graphene.Boolean(required=True)
    template_data = JSONString(
        description="Theme template data (CSS variables, fonts, colors, etc.)"
    )
    preview_image = graphene.Field(Image)
    created_at = DateTime(required=True)
    updated_at = DateTime(required=True)


class ThemeVersion(ModelObjectType[models.ThemeVersion]):
    """Version history for themes, enabling rollback functionality."""

    class Meta:
        description = "Version history for themes, enabling rollback functionality."
        model = models.ThemeVersion
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    theme = graphene.Field(Theme, required=True)
    version_number = graphene.Int(required=True)
    template_data = JSONString(
        description="Snapshot of template data at this version"
    )
    notes = graphene.String()
    created_at = DateTime(required=True)


class SellerStorefrontSettings(ModelObjectType[models.SellerStorefrontSettings]):
    """Storefront-specific settings and branding for a seller."""

    class Meta:
        description = "Storefront settings and branding for a seller."
        model = models.SellerStorefrontSettings
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    seller = graphene.Field(Seller, required=True)
    theme = graphene.Field(Theme, description="Active theme for this seller's storefront")
    theme_customizations = JSONString(
        description="Customizations to the theme template (overrides template_data)"
    )
    primary_color = graphene.String()
    secondary_color = graphene.String()
    favicon = graphene.Field(Image)
    storefront_logo = graphene.Field(Image)
    custom_css = graphene.String()
    meta_title = graphene.String()
    meta_description = graphene.String()
    facebook_url = graphene.String()
    twitter_url = graphene.String()
    instagram_url = graphene.String()
    contact_email = graphene.String()
    contact_phone = graphene.String()
    created_at = DateTime(required=True)
    updated_at = DateTime(required=True)


class NewsletterSubscription(ModelObjectType[models.NewsletterSubscription]):
    """Newsletter subscription for customers."""

    class Meta:
        description = "Newsletter subscription for customers."
        model = models.NewsletterSubscription
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    email = graphene.String(required=True)
    is_active = graphene.Boolean(required=True)
    confirmed_at = DateTime()
    unsubscribed_at = DateTime()
    source = graphene.String()
    user = graphene.Field("saleor.graphql.account.types.User")
    created_at = DateTime(required=True)
    updated_at = DateTime(required=True)


class FulfillmentCenter(ModelObjectType[models.FulfillmentCenter]):
    """Represents a HoS-operated fulfillment center."""

    class Meta:
        description = "Represents a fulfillment center (Liverpool UK, USA, Malaysia, UAE, etc.)"
        model = models.FulfillmentCenter
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    location = graphene.String(required=True)
    country = graphene.Field(CountryDisplay)
    address = graphene.Field("saleor.graphql.account.types.Address")
    is_active = graphene.Boolean(required=True)
    priority = graphene.Int(required=True)


class SellerLogisticsConfig(ModelObjectType[models.SellerLogisticsConfig]):
    """Logistics configuration for a seller."""

    class Meta:
        description = "Logistics configuration for a seller"
        model = models.SellerLogisticsConfig
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    seller = graphene.Field(Seller, required=True)
    fulfillment_method = FulfillmentMethodEnum(required=True)
    primary_fulfillment_center = graphene.Field(FulfillmentCenter)
    shipping_provider = graphene.String()
    handling_time_days = graphene.Int(required=True)
    free_shipping_threshold = Decimal()
    custom_shipping_methods = JSONString()
    logistics_partner_integration = JSONString()


class SellerShippingMethod(ModelObjectType[models.SellerShippingMethod]):
    """Seller-specific shipping method."""

    class Meta:
        description = "Seller-specific shipping method with custom rates"
        model = models.SellerShippingMethod
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    seller = graphene.Field(Seller, required=True)
    name = graphene.String(required=True)
    price = graphene.Field(Money, required=False)
    estimated_days = graphene.Int()
    is_active = graphene.Boolean(required=True)
    fulfillment_center = graphene.Field(FulfillmentCenter)
    destination_country = graphene.Field(CountryDisplay)
    destination_city = graphene.String()
    tiered_pricing = JSONString()


class ProductSubmission(ModelObjectType[models.ProductSubmission]):
    """Product submission for admin approval."""

    class Meta:
        description = "Product submission by seller for admin approval"
        model = models.ProductSubmission
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    seller = graphene.Field(Seller, required=True)
    product = graphene.Field("saleor.graphql.product.types.products.Product", required=True)
    submitted_at = DateTime(required=True)
    status = ProductApprovalStatusEnum(required=True)
    admin_notes = graphene.String()
    reviewed_by = graphene.Field("saleor.graphql.account.types.User")
    reviewed_at = DateTime()


class ReturnPolicy(ModelObjectType[models.ReturnPolicy]):
    """Return policy for sellers or products."""

    class Meta:
        description = "Return policy configuration"
        model = models.ReturnPolicy
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    seller = graphene.Field(Seller)
    product = graphene.Field("saleor.graphql.product.types.products.Product")
    return_period_days = graphene.Int(required=True)
    return_conditions = JSONString()
    return_shipping_cost = graphene.String(required=True)
    is_active = graphene.Boolean(required=True)


class ReturnRequest(ModelObjectType[models.ReturnRequest]):
    """Return request from a customer."""

    class Meta:
        description = "Return request from a customer"
        model = models.ReturnRequest
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    order = graphene.Field("saleor.graphql.order.types.Order", required=True)
    order_line = graphene.Field("saleor.graphql.order.types.OrderLine", required=True)
    user = graphene.Field("saleor.graphql.account.types.User", required=True)
    reason = graphene.String(required=True)
    notes = graphene.String(description="Additional notes for the return request.")
    status = ReturnRequestStatusEnum(required=True)
    requested_at = DateTime(required=True)
    created = DateTime(description="Alias for requested_at.")
    processed_at = DateTime()
    processed_by = graphene.Field("saleor.graphql.account.types.User")
    order_id = graphene.ID(description="ID of the order for this return request.")

    @staticmethod
    def resolve_notes(root: models.ReturnRequest, info):
        """Resolve notes from metadata."""
        return root.get_value_from_metadata("notes", "")

    @staticmethod
    def resolve_created(root: models.ReturnRequest, info):
        """Alias for requested_at."""
        return root.requested_at

    @staticmethod
    def resolve_order_id(root: models.ReturnRequest, info):
        """Return the order ID as a GlobalID."""
        from ..core.utils import to_global_id_or_none
        from ..order.types import Order
        
        return to_global_id_or_none(Order, root.order_id)


class FulfillmentCenterCountableConnection(CountableConnection):
    """Connection type for FulfillmentCenter list queries."""

    class Meta:
        node = FulfillmentCenter
        doc_category = DOC_CATEGORY_MARKETPLACE


class ProductSubmissionCountableConnection(CountableConnection):
    """Connection type for ProductSubmission list queries."""

    class Meta:
        node = ProductSubmission
        doc_category = DOC_CATEGORY_MARKETPLACE


class SellerShippingMethodCountableConnection(CountableConnection):
    """Connection type for SellerShippingMethod list queries."""

    class Meta:
        node = SellerShippingMethod
        doc_category = DOC_CATEGORY_MARKETPLACE


class ReturnRequestCountableConnection(CountableConnection):
    """Connection type for ReturnRequest list queries."""

    class Meta:
        node = ReturnRequest
        doc_category = DOC_CATEGORY_MARKETPLACE


class ReturnPolicyCountableConnection(CountableConnection):
    """Connection type for ReturnPolicy list queries."""

    class Meta:
        node = ReturnPolicy
        doc_category = DOC_CATEGORY_MARKETPLACE


class PricingRule(ModelObjectType[models.PricingRule]):
    """HoS pricing control rule."""

    class Meta:
        description = "Pricing rule for products (RRP, promotional, seasonal)"
        model = models.PricingRule
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    product = graphene.Field("saleor.graphql.product.types.products.Product")
    seller = graphene.Field(Seller)
    pricing_type = PricingTypeEnum(required=True)
    discount_percentage = Decimal()
    fixed_price = graphene.Field(Money)
    valid_from = DateTime()
    valid_until = DateTime()
    country = graphene.Field(CountryDisplay)
    is_active = graphene.Boolean(required=True)


class PaymentGatewayConfig(ModelObjectType[models.PaymentGatewayConfig]):
    """Payment gateway configuration."""

    class Meta:
        description = "Payment gateway configuration for sellers"
        model = models.PaymentGatewayConfig
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    seller = graphene.Field(Seller)
    gateway_name = graphene.String(required=True)
    gateway_config = JSONString()
    enabled_countries = graphene.List(CountryDisplay)
    enabled_currencies = graphene.List(graphene.String)
    compliance_requirements = JSONString()
    is_active = graphene.Boolean(required=True)


class UserPreferences(graphene.ObjectType):
    """User preferences stored in user metadata."""

    class Meta:
        description = "User preferences for theme, language, currency, and other settings."
        doc_category = DOC_CATEGORY_MARKETPLACE

    theme_id = graphene.ID(description="Preferred theme ID.")
    language_code = graphene.String(description="Preferred language code (e.g., 'en', 'es').")
    currency_code = graphene.String(description="Preferred currency code (e.g., 'USD', 'EUR').")
    timezone = graphene.String(description="Preferred timezone (e.g., 'America/New_York').")
    email_notifications = graphene.Boolean(
        description="Whether to receive email notifications (defaults to True)."
    )
    marketing_emails = graphene.Boolean(
        description="Whether to receive marketing emails (defaults to False)."
    )
    recently_viewed_products_limit = graphene.Int(
        description="Maximum number of recently viewed products to keep (defaults to 10)."
    )
