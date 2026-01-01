"""GraphQL input types for marketplace."""

import graphene

from ..core.doc_category import DOC_CATEGORY_MARKETPLACE
from ..core.fields import JSONString
from ..core.scalars import Decimal
from ..core.types import BaseInputObjectType, Upload
from .enums import SellerStatusEnum


class SellerCreateInput(BaseInputObjectType):
    """Input type for creating a seller."""

    store_name = graphene.String(required=True, description="Store name of the seller.")
    slug = graphene.String(
        description="Slug for the seller's store (auto-generated if not provided)."
    )
    description = graphene.String(description="Description of the seller.")
    status = SellerStatusEnum(
        description="Status of the seller account (defaults to PENDING)."
    )
    platform_fee_percentage = Decimal(
        description="Platform fee percentage (e.g., 10.00 for 10%, defaults to 10.00)."
    )
    stripe_account_id = graphene.String(
        description="Stripe Connect account ID for payouts."
    )
    tax_origin_address_id = graphene.ID(
        description="ID of the address used as tax origin for this seller."
    )

    class Meta:
        doc_category = DOC_CATEGORY_MARKETPLACE


class SellerUpdateInput(BaseInputObjectType):
    """Input type for updating a seller."""

    store_name = graphene.String(description="Store name of the seller.")
    slug = graphene.String(description="Slug for the seller's store.")
    description = graphene.String(description="Description of the seller.")
    status = SellerStatusEnum(description="Status of the seller account.")
    platform_fee_percentage = Decimal(
        description="Platform fee percentage (e.g., 10.00 for 10%)."
    )
    stripe_account_id = graphene.String(
        description="Stripe Connect account ID for payouts."
    )
    tax_origin_address_id = graphene.ID(
        description="ID of the address used as tax origin for this seller."
    )
    minimum_order_quantity = graphene.Int(
        description="Minimum order quantity for B2B sellers."
    )
    credit_terms_enabled = graphene.Boolean(
        description="Whether credit terms are enabled for B2B sellers."
    )

    class Meta:
        doc_category = DOC_CATEGORY_MARKETPLACE


class SellerShippingMethodInput(BaseInputObjectType):
    """Input type for seller shipping method."""

    name = graphene.String(required=True, description="Name of the shipping method.")
    price = Decimal(required=True, description="Shipping price.")
    estimated_days = graphene.Int(description="Estimated delivery time in days.")
    is_active = graphene.Boolean(
        description="Whether this shipping method is active.", default_value=True
    )
    fulfillment_center_id = graphene.ID(
        description="ID of the fulfillment center."
    )
    destination_country = graphene.String(
        description="Destination country code (ISO 3166-1 alpha-2)."
    )
    destination_city = graphene.String(description="Destination city.")
    tiered_pricing = JSONString(
        description="Tiered pricing configuration (JSON)."
    )

    class Meta:
        doc_category = DOC_CATEGORY_MARKETPLACE


class NewsletterSubscribeInput(BaseInputObjectType):
    """Input type for newsletter subscription."""

    email = graphene.String(required=True, description="Email address to subscribe.")
    source = graphene.String(
        description="Source of the subscription (e.g., 'homepage', 'footer', 'checkout')."
    )

    class Meta:
        doc_category = DOC_CATEGORY_MARKETPLACE


class SellerDomainInput(BaseInputObjectType):
    """Input type for seller domain."""

    domain = graphene.String(
        required=True, description="Domain name (e.g., store.example.com or example.com)."
    )
    is_primary = graphene.Boolean(
        description="Whether this is the primary domain for the seller.",
        default_value=False,
    )
    ssl_enabled = graphene.Boolean(
        description="Whether SSL is enabled for this domain.",
        default_value=False,
    )

    class Meta:
        doc_category = DOC_CATEGORY_MARKETPLACE


class ThemeCreateInput(BaseInputObjectType):
    """Input type for creating a theme."""

    name = graphene.String(required=True, description="Name of the theme.")
    slug = graphene.String(description="Slug for the theme (auto-generated if not provided).")
    description = graphene.String(description="Description of the theme.")
    is_default = graphene.Boolean(
        description="Whether this is the default theme.",
        default_value=False,
    )
    is_active = graphene.Boolean(
        description="Whether this theme is active.",
        default_value=True,
    )
    template_data = JSONString(
        description="Theme template data (CSS variables, fonts, colors, etc.) as JSON."
    )
    preview_image = Upload(description="Preview image for the theme.")

    class Meta:
        doc_category = DOC_CATEGORY_MARKETPLACE


class ThemeUpdateInput(BaseInputObjectType):
    """Input type for updating a theme."""

    name = graphene.String(description="Name of the theme.")
    slug = graphene.String(description="Slug for the theme.")
    description = graphene.String(description="Description of the theme.")
    is_default = graphene.Boolean(description="Whether this is the default theme.")
    is_active = graphene.Boolean(description="Whether this theme is active.")
    template_data = JSONString(
        description="Theme template data (CSS variables, fonts, colors, etc.) as JSON."
    )
    preview_image = Upload(description="Preview image for the theme.")

    class Meta:
        doc_category = DOC_CATEGORY_MARKETPLACE


class UserPreferencesInput(BaseInputObjectType):
    """Input type for user preferences."""

    theme_id = graphene.ID(description="ID of the preferred theme.")
    language_code = graphene.String(description="Preferred language code (e.g., 'en', 'es').")
    currency_code = graphene.String(description="Preferred currency code (e.g., 'USD', 'EUR').")
    timezone = graphene.String(description="Preferred timezone (e.g., 'America/New_York').")
    email_notifications = graphene.Boolean(
        description="Whether to receive email notifications.",
        default_value=True,
    )
    marketing_emails = graphene.Boolean(
        description="Whether to receive marketing emails.",
        default_value=False,
    )
    recently_viewed_products_limit = graphene.Int(
        description="Maximum number of recently viewed products to store.",
        default_value=20,
    )

    class Meta:
        doc_category = DOC_CATEGORY_MARKETPLACE


class SellerStorefrontSettingsInput(BaseInputObjectType):
    """Input type for seller storefront settings."""

    theme_id = graphene.ID(description="ID of the theme to use for the storefront.")
    custom_css = graphene.String(description="Custom CSS for the storefront.")
    custom_js = graphene.String(description="Custom JavaScript for the storefront.")
    header_html = graphene.String(description="Custom HTML for the header.")
    footer_html = graphene.String(description="Custom HTML for the footer.")
    homepage_layout = JSONString(description="Homepage layout configuration as JSON.")
    navigation_config = JSONString(description="Navigation configuration as JSON.")

    class Meta:
        doc_category = DOC_CATEGORY_MARKETPLACE
