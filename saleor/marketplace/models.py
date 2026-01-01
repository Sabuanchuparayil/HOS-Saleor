"""Marketplace models for multi-vendor functionality."""

# Import loyalty models for easier access
from .models_loyalty import (  # noqa: F401
    Badge,
    LoyaltyPointsBalance,
    LoyaltyPointsTransaction,
    Reward,
    RewardRedemption,
    UserBadge,
)

# Import fandom models for easier access
from .models_fandom import (  # noqa: F401
    FandomCharacter,
    ProductCharacter,
    Quiz,
    QuizSubmission,
)

# Import help center models for easier access
from .models_help import (  # noqa: F401
    ContactSupportTicket,
    ContactSupportTicketMessage,
    HelpArticle,
    HelpArticleView,
    HelpCategory,
)

# Import discount config model
from .models_discount import SellerDiscountConfig  # noqa: F401

from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.contrib.postgres.indexes import BTreeIndex, GinIndex
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django_countries.fields import CountryField

from ..account.models import Address, User
from ..channel.models import Channel
from ..core.models import ModelWithMetadata, ModelWithExternalReference
from ..shipping.models import ShippingZone
from ..warehouse.models import Warehouse


class SellerStatus(models.TextChoices):
    """Status choices for Seller account."""

    PENDING = "pending", "Pending"
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    DEACTIVATED = "deactivated", "Deactivated"


class SellerType(models.TextChoices):
    """Business model type for Seller."""

    B2B_WHOLESALE = "b2b_wholesale", "B2B Wholesale"
    B2C_RETAIL = "b2c_retail", "B2C Retail"
    HYBRID = "hybrid", "Hybrid (B2B & B2C)"


class DistributorCategory(models.TextChoices):
    """Category for authorized distributors."""

    B2C_DISTRIBUTOR = "b2c_distributor", "B2C Distributor (Single-piece retail)"
    WHOLESALE_DISTRIBUTOR = "wholesale_distributor", "Wholesale Distributor (Bulk sales only)"


class Seller(ModelWithMetadata, ModelWithExternalReference):
    """Represents a seller/vendor in the marketplace."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Store information
    store_name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="seller-logos", blank=True, null=True)

    # Owner and staff
    owner = models.ForeignKey(
        User,
        related_name="owned_sellers",
        on_delete=models.PROTECT,
        help_text="Primary owner/admin of the seller account",
    )
    staff = models.ManyToManyField(
        User,
        related_name="seller_staff",
        blank=True,
        help_text="Additional staff members with seller access",
    )

    # Status
    status = models.CharField(
        max_length=32, choices=SellerStatus.choices, default=SellerStatus.PENDING
    )

    # Business model and seller type
    seller_type = models.CharField(
        max_length=32,
        choices=SellerType.choices,
        default=SellerType.B2C_RETAIL,
        help_text="Business model type: B2B Wholesale, B2C Retail, or Hybrid",
    )
    is_authorized_distributor = models.BooleanField(
        default=False,
        help_text="Whether this seller is an authorized distributor",
    )
    distributor_category = models.CharField(
        max_length=32,
        choices=DistributorCategory.choices,
        blank=True,
        null=True,
        help_text="Category for authorized distributors (B2C or Wholesale)",
    )
    minimum_order_quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Minimum order quantity for B2B/wholesale sellers",
    )
    credit_terms_enabled = models.BooleanField(
        default=False,
        help_text="Whether credit terms (net 30, net 60, etc.) are enabled for B2B sellers",
    )
    business_registration_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Business registration number for B2B verification",
    )

    # Channel relationship (for multi-tenancy)
    channel = models.OneToOneField(
        Channel,
        related_name="seller",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Dedicated channel for this seller's storefront",
    )

    # Financial settings
    platform_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("10.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    # Settlement settings
    stripe_account_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Stripe Connect account ID for payouts",
    )

    # Tax settings
    tax_origin_address = models.ForeignKey(
        Address,
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Default address used as tax origin for this seller",
    )

    class Meta:
        app_label = "marketplace"
        ordering = ("store_name", "created_at")
        indexes = [
            *ModelWithMetadata.Meta.indexes,
            BTreeIndex(fields=["status"], name="seller_status_idx"),
            BTreeIndex(fields=["created_at"], name="seller_created_at_idx"),
            BTreeIndex(fields=["owner"], name="seller_owner_idx"),
            BTreeIndex(fields=["slug"], name="seller_slug_idx"),
            BTreeIndex(fields=["seller_type"], name="seller_type_idx"),
            BTreeIndex(fields=["is_authorized_distributor"], name="seller_authorized_idx"),
            GinIndex(
                fields=["store_name", "slug"],
                name="seller_search_gin",
                opclasses=["gin_trgm_ops"] * 2,
            ),
        ]

    def __str__(self):
        return self.store_name

    @property
    def is_active(self):
        return self.status == SellerStatus.ACTIVE


class SellerDomainStatus(models.TextChoices):
    """Status choices for seller domain."""

    PENDING = "pending", "Pending Verification"
    VERIFIED = "verified", "Verified"
    ACTIVE = "active", "Active"
    FAILED = "failed", "Verification Failed"
    INACTIVE = "inactive", "Inactive"


class SellerDomain(ModelWithMetadata):
    """Represents a custom domain or subdomain for a seller's storefront."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    seller = models.ForeignKey(
        Seller,
        related_name="domains",
        on_delete=models.CASCADE,
        help_text="Seller who owns this domain",
    )
    domain = models.CharField(
        max_length=255,
        unique=True,
        help_text="Custom domain (e.g., store.example.com or example.com)",
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
                message="Invalid domain format",
            )
        ],
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Primary domain for this seller (only one per seller)",
    )
    status = models.CharField(
        max_length=32,
        choices=SellerDomainStatus.choices,
        default=SellerDomainStatus.PENDING,
    )
    verification_token = models.CharField(
        max_length=255,
        blank=True,
        help_text="Token for domain verification",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    ssl_enabled = models.BooleanField(
        default=False,
        help_text="Whether SSL certificate is enabled for this domain",
    )
    ssl_certificate_issued_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "marketplace"
        ordering = ("seller", "-is_primary", "domain")
        indexes = [
            BTreeIndex(fields=["seller"], name="seller_domain_seller_idx"),
            BTreeIndex(fields=["domain"], name="seller_domain_domain_idx"),
            BTreeIndex(fields=["status"], name="seller_domain_status_idx"),
            BTreeIndex(fields=["is_primary"], name="seller_domain_primary_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["seller", "is_primary"],
                condition=models.Q(is_primary=True),
                name="unique_primary_domain_per_seller",
            )
        ]

    def __str__(self):
        return f"{self.domain} ({self.seller.store_name})"


class Theme(ModelWithMetadata):
    """Theme template definition for storefront customization."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is the HOS default theme",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this theme is available for use",
    )
    # Template data stored as JSON (CSS variables, fonts, layouts, etc.)
    template_data = models.JSONField(
        default=dict,
        help_text="Theme template data (CSS variables, fonts, colors, etc.)",
    )
    preview_image = models.ImageField(
        upload_to="theme-previews", blank=True, null=True
    )

    class Meta:
        app_label = "marketplace"
        ordering = ("name",)
        indexes = [
            BTreeIndex(fields=["is_default"], name="theme_default_idx"),
            BTreeIndex(fields=["is_active"], name="theme_active_idx"),
            BTreeIndex(fields=["slug"], name="theme_slug_idx"),
        ]

    def __str__(self):
        return self.name


class ThemeVersion(ModelWithMetadata):
    """Version history for themes, enabling rollback functionality."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    theme = models.ForeignKey(
        Theme,
        related_name="versions",
        on_delete=models.CASCADE,
    )
    version_number = models.IntegerField()
    template_data = models.JSONField(
        default=dict,
        help_text="Snapshot of template data at this version",
    )
    notes = models.TextField(blank=True, help_text="Release notes for this version")

    class Meta:
        app_label = "marketplace"
        ordering = ("-version_number",)
        indexes = [
            BTreeIndex(fields=["theme", "version_number"], name="theme_version_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["theme", "version_number"],
                name="unique_theme_version",
            )
        ]

    def __str__(self):
        return f"{self.theme.name} v{self.version_number}"


class SellerStorefrontSettings(ModelWithMetadata):
    """Storefront-specific settings and branding for a seller."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    seller = models.OneToOneField(
        Seller,
        related_name="storefront_settings",
        on_delete=models.CASCADE,
    )
    
    # Theme relationship
    theme = models.ForeignKey(
        Theme,
        related_name="seller_settings",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Active theme for this seller's storefront",
    )
    theme_customizations = models.JSONField(
        default=dict,
        help_text="Customizations to the theme template (overrides template_data)",
    )
    
    # Branding (kept for backward compatibility, can be moved to theme_customizations)
    primary_color = models.CharField(
        max_length=7,
        blank=True,
        default="#000000",
        help_text="Primary brand color (hex)",
        validators=[RegexValidator(regex=r"^#[0-9A-Fa-f]{6}$", message="Invalid hex color")],
    )
    secondary_color = models.CharField(
        max_length=7,
        blank=True,
        default="#FFFFFF",
        help_text="Secondary brand color (hex)",
        validators=[RegexValidator(regex=r"^#[0-9A-Fa-f]{6}$", message="Invalid hex color")],
    )
    favicon = models.ImageField(upload_to="seller-favicons", blank=True, null=True)
    storefront_logo = models.ImageField(
        upload_to="seller-storefront-logos", blank=True, null=True
    )
    # Custom CSS
    custom_css = models.TextField(
        blank=True,
        help_text="Custom CSS for storefront customization",
    )
    # SEO
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    # Social links
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    # Contact info
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=255, blank=True)

    class Meta:
        app_label = "marketplace"
        ordering = ("seller",)
        indexes = [
            BTreeIndex(fields=["theme"], name="seller_settings_theme_idx"),
        ]

    def __str__(self):
        return f"Storefront settings for {self.seller.store_name}"


class TaxRegistrationType(models.TextChoices):
    """Type of tax registration."""

    VAT = "vat", "VAT"
    GST = "gst", "GST"
    SALES_TAX = "sales_tax", "Sales Tax"
    OTHER = "other", "Other"


class SellerTaxRegistration(ModelWithMetadata):
    """Represents a tax registration for a seller in a specific country/region."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    seller = models.ForeignKey(
        Seller, related_name="tax_registrations", on_delete=models.CASCADE
    )
    registration_type = models.CharField(
        max_length=32, choices=TaxRegistrationType.choices
    )
    registration_number = models.CharField(max_length=255)
    country = CountryField()
    region = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "marketplace"
        ordering = ("seller", "country", "registration_type")
        constraints = [
            models.UniqueConstraint(
                fields=("seller", "registration_type", "country", "region"),
                name="unique_seller_tax_registration",
            )
        ]
        indexes = [
            BTreeIndex(fields=["seller"], name="seller_tax_reg_seller_idx"),
            BTreeIndex(fields=["country"], name="seller_tax_reg_country_idx"),
            BTreeIndex(fields=["is_active"], name="seller_tax_reg_active_idx"),
        ]

    def __str__(self):
        return f"{self.seller.store_name} - {self.registration_type} ({self.country})"


class SellerWarehouse(ModelWithMetadata):
    """Represents a seller's assigned warehouse/fulfillment center."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    seller = models.ForeignKey(
        Seller,
        related_name="warehouses",
        on_delete=models.CASCADE,
        help_text="Seller who has access to this warehouse",
    )
    warehouse = models.ForeignKey(
        Warehouse,
        related_name="sellers",
        on_delete=models.CASCADE,
        help_text="Warehouse/fulfillment center",
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Primary fulfillment center for this seller",
    )
    priority = models.IntegerField(
        default=0,
        help_text="Priority for fulfillment (lower number = higher priority)",
    )

    class Meta:
        app_label = "marketplace"
        ordering = ("seller", "priority", "warehouse")
        indexes = [
            BTreeIndex(fields=["seller"], name="seller_warehouse_seller_idx"),
            BTreeIndex(fields=["warehouse"], name="seller_warehouse_warehouse_idx"),
            BTreeIndex(fields=["is_primary"], name="seller_warehouse_primary_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["seller", "warehouse"],
                name="unique_seller_warehouse",
            )
        ]

    def __str__(self):
        return f"{self.seller.store_name} -> {self.warehouse.name}"


class FulfillmentCenter(ModelWithMetadata):
    """Represents HoS-operated logistics centers (Liverpool UK, USA, Malaysia, UAE, etc.)."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=255, help_text="Name of the fulfillment center")
    location = models.CharField(
        max_length=255, help_text="Location description (e.g., 'Liverpool, UK')"
    )
    country = CountryField(help_text="Country where the center is located")
    address = models.ForeignKey(
        Address,
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Full address of the fulfillment center",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this fulfillment center is active"
    )
    priority = models.IntegerField(
        default=0,
        help_text="Priority for order routing (lower number = higher priority)",
    )
    warehouses = models.ManyToManyField(
        Warehouse,
        related_name="fulfillment_centers",
        blank=True,
        help_text="Saleor warehouses linked to this fulfillment center",
    )

    class Meta:
        app_label = "marketplace"
        ordering = ("priority", "name")
        indexes = [
            BTreeIndex(fields=["country"], name="fulfillment_center_country_idx"),
            BTreeIndex(fields=["is_active"], name="fulfillment_center_active_idx"),
            BTreeIndex(fields=["priority"], name="fulfillment_center_priority_idx"),
        ]

    def __str__(self):
        return f"{self.name} ({self.location})"


class FulfillmentMethod(models.TextChoices):
    """Fulfillment method choices."""

    SELF_FULFILL = "self_fulfill", "Self Fulfill"
    DROPSHIP = "dropship", "Dropship"
    MARKETPLACE_FULFILL = "marketplace_fulfill", "Marketplace Fulfill"
    THIRD_PARTY = "third_party", "Third Party"


class SellerLogisticsConfig(ModelWithMetadata):
    """Logistics configuration for a seller."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    seller = models.OneToOneField(
        Seller,
        related_name="logistics_config",
        on_delete=models.CASCADE,
        help_text="Seller this configuration belongs to",
    )
    fulfillment_method = models.CharField(
        max_length=32,
        choices=FulfillmentMethod.choices,
        default=FulfillmentMethod.MARKETPLACE_FULFILL,
        help_text="Method used for order fulfillment",
    )
    primary_fulfillment_center = models.ForeignKey(
        FulfillmentCenter,
        related_name="sellers",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Primary fulfillment center for this seller",
    )
    shipping_provider = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Shipping provider/carrier integration name",
    )
    handling_time_days = models.PositiveIntegerField(
        default=3,
        help_text="Number of days to handle/process orders (B2C: 1-3 days, B2B: 5-10 days)",
    )
    free_shipping_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Order value threshold for free shipping (different for B2B vs B2C)",
    )
    shipping_zones = models.ManyToManyField(
        ShippingZone,
        related_name="seller_logistics_configs",
        blank=True,
        help_text="Shipping zones this seller can ship to",
    )
    custom_shipping_methods = models.JSONField(
        default=dict,
        blank=True,
        help_text="Seller-specific shipping rates and methods (JSON)",
    )
    logistics_partner_integration = models.JSONField(
        default=dict,
        blank=True,
        help_text="Global logistics partner configuration (JSON)",
    )

    class Meta:
        app_label = "marketplace"
        ordering = ("seller",)
        indexes = [
            BTreeIndex(
                fields=["fulfillment_method"], name="logistics_config_method_idx"
            ),
            BTreeIndex(
                fields=["primary_fulfillment_center"],
                name="logistics_config_center_idx",
            ),
        ]

    def __str__(self):
        return f"Logistics config for {self.seller.store_name}"


class SellerShippingMethod(ModelWithMetadata):
    """Seller-specific shipping method with custom rates."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    seller = models.ForeignKey(
        Seller,
        related_name="shipping_methods",
        on_delete=models.CASCADE,
        help_text="Seller who owns this shipping method",
    )
    name = models.CharField(max_length=255, help_text="Name of the shipping method")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Shipping price (base rate)",
    )
    estimated_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Estimated delivery time in days",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this shipping method is active"
    )
    fulfillment_center = models.ForeignKey(
        FulfillmentCenter,
        related_name="shipping_methods",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Fulfillment center this method applies to (optional)",
    )
    destination_country = CountryField(
        null=True,
        blank=True,
        help_text="Destination country for dynamic calculation (optional)",
    )
    destination_city = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Destination city for dynamic calculation (optional)",
    )
    tiered_pricing = models.JSONField(
        default=dict,
        blank=True,
        help_text="Tiered pricing rules by weight/price (JSON)",
    )

    class Meta:
        app_label = "marketplace"
        ordering = ("seller", "name")
        indexes = [
            BTreeIndex(fields=["seller"], name="seller_shipping_seller_idx"),
            BTreeIndex(fields=["is_active"], name="seller_shipping_active_idx"),
            BTreeIndex(
                fields=["destination_country"], name="seller_shipping_country_idx"
            ),
        ]

    def __str__(self):
        return f"{self.name} - {self.seller.store_name}"


class OrderRoutingRule(ModelWithMetadata):
    """Rules for automatic order routing to fulfillment centers."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(
        max_length=255, help_text="Name/description of the routing rule"
    )
    fulfillment_center = models.ForeignKey(
        FulfillmentCenter,
        related_name="routing_rules",
        on_delete=models.CASCADE,
        help_text="Fulfillment center this rule routes to",
    )
    priority = models.IntegerField(
        default=0,
        help_text="Priority for this rule (lower number = higher priority)",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this routing rule is active"
    )
    # Routing conditions stored as JSON
    conditions = models.JSONField(
        default=dict,
        help_text="Routing conditions: inventory availability, delivery location, seller preference (JSON)",
    )

    class Meta:
        app_label = "marketplace"
        ordering = ("priority", "name")
        indexes = [
            BTreeIndex(fields=["fulfillment_center"], name="routing_rule_center_idx"),
            BTreeIndex(fields=["priority"], name="routing_rule_priority_idx"),
            BTreeIndex(fields=["is_active"], name="routing_rule_active_idx"),
        ]

    def __str__(self):
        return f"{self.name} -> {self.fulfillment_center.name}"


class ProductApprovalStatus(models.TextChoices):
    """Status choices for product approval workflow."""

    PENDING = "pending", "Pending Approval"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    REQUIRES_REVISION = "requires_revision", "Requires Revision"


class ProductSubmission(ModelWithMetadata):
    """Tracks products submitted by sellers for admin approval."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    seller = models.ForeignKey(
        Seller,
        related_name="product_submissions",
        on_delete=models.CASCADE,
        help_text="Seller who submitted this product",
    )
    product = models.ForeignKey(
        "product.Product",
        related_name="submissions",
        on_delete=models.CASCADE,
        help_text="Product being submitted",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=32,
        choices=ProductApprovalStatus.choices,
        default=ProductApprovalStatus.PENDING,
    )
    admin_notes = models.TextField(
        blank=True, help_text="Admin notes on approval/rejection"
    )
    reviewed_by = models.ForeignKey(
        User,
        related_name="product_submissions_reviewed",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Admin user who reviewed this submission",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "marketplace"
        ordering = ("-submitted_at",)
        indexes = [
            BTreeIndex(fields=["seller"], name="product_submission_seller_idx"),
            BTreeIndex(fields=["status"], name="product_submission_status_idx"),
            BTreeIndex(fields=["submitted_at"], name="product_submission_date_idx"),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.seller.store_name} ({self.status})"


class ReturnPolicy(ModelWithMetadata):
    """Return policy configuration for sellers or products."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    seller = models.ForeignKey(
        Seller,
        related_name="return_policies",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Seller this policy applies to (optional, for seller-specific policies)",
    )
    product = models.ForeignKey(
        "product.Product",
        related_name="return_policies",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Product this policy applies to (optional, for SKU-specific policies)",
    )
    return_period_days = models.PositiveIntegerField(
        help_text="Number of days within which returns are accepted"
    )
    return_conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Return requirements and conditions (JSON)",
    )
    return_shipping_cost = models.CharField(
        max_length=32,
        choices=[
            ("customer", "Customer pays"),
            ("seller", "Seller pays"),
            ("free", "Free return shipping"),
        ],
        default="customer",
        help_text="Who pays for return shipping",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this return policy is active"
    )

    class Meta:
        app_label = "marketplace"
        ordering = ("seller", "product", "return_period_days")
        indexes = [
            BTreeIndex(fields=["seller"], name="return_policy_seller_idx"),
            BTreeIndex(fields=["product"], name="return_policy_product_idx"),
            BTreeIndex(fields=["is_active"], name="return_policy_active_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(seller__isnull=True, product__isnull=True),
                name="return_policy_requires_seller_or_product",
            )
        ]

    def __str__(self):
        if self.product:
            return f"Return policy for {self.product.name} ({self.return_period_days} days)"
        return f"Return policy for {self.seller.store_name} ({self.return_period_days} days)"


class ReturnRequestStatus(models.TextChoices):
    """Status choices for return requests."""

    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class ReturnRequest(ModelWithMetadata):
    """Return request from a customer."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    order = models.ForeignKey(
        "order.Order",
        related_name="return_requests",
        on_delete=models.CASCADE,
        help_text="Order this return is for",
    )
    order_line = models.ForeignKey(
        "order.OrderLine",
        related_name="return_requests",
        on_delete=models.CASCADE,
        help_text="Order line being returned",
    )
    user = models.ForeignKey(
        User,
        related_name="return_requests",
        on_delete=models.CASCADE,
        help_text="Customer requesting the return",
    )
    reason = models.TextField(help_text="Reason for return")
    status = models.CharField(
        max_length=32,
        choices=ReturnRequestStatus.choices,
        default=ReturnRequestStatus.PENDING,
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        User,
        related_name="return_requests_processed",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Staff member who processed this return",
    )

    class Meta:
        app_label = "marketplace"
        ordering = ("-requested_at",)
        indexes = [
            BTreeIndex(fields=["order"], name="return_request_order_idx"),
            BTreeIndex(fields=["user"], name="return_request_user_idx"),
            BTreeIndex(fields=["status"], name="return_request_status_idx"),
            BTreeIndex(fields=["requested_at"], name="return_request_date_idx"),
        ]

    def __str__(self):
        return f"Return #{self.id} - {self.order.number} ({self.status})"


class InventorySync(ModelWithMetadata):
    """Tracks inventory synchronization between fulfillment centers and seller dashboards."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    product_variant = models.ForeignKey(
        "product.ProductVariant",
        related_name="inventory_syncs",
        on_delete=models.CASCADE,
        help_text="Product variant being synced",
    )
    fulfillment_center = models.ForeignKey(
        FulfillmentCenter,
        related_name="inventory_syncs",
        on_delete=models.CASCADE,
        help_text="Fulfillment center this sync is for",
    )
    warehouse = models.ForeignKey(
        Warehouse,
        related_name="inventory_syncs",
        on_delete=models.CASCADE,
        help_text="Warehouse being synced",
    )
    quantity_available = models.IntegerField(
        default=0, help_text="Available quantity at time of sync"
    )
    quantity_reserved = models.IntegerField(
        default=0, help_text="Reserved quantity at time of sync"
    )
    synced_at = models.DateTimeField(auto_now_add=True)
    sync_method = models.CharField(
        max_length=32,
        choices=[
            ("webhook", "Webhook"),
            ("polling", "Polling"),
            ("manual", "Manual"),
        ],
        default="polling",
        help_text="Method used for synchronization",
    )

    class Meta:
        app_label = "marketplace"
        ordering = ("-synced_at",)
        indexes = [
            BTreeIndex(fields=["product_variant"], name="inventory_sync_variant_idx"),
            BTreeIndex(
                fields=["fulfillment_center"], name="inventory_sync_center_idx"
            ),
            BTreeIndex(fields=["synced_at"], name="inventory_sync_date_idx"),
        ]

    def __str__(self):
        return f"Sync: {self.product_variant.sku} @ {self.fulfillment_center.name}"


class PricingType(models.TextChoices):
    """Pricing rule type choices."""

    RRP = "rrp", "Recommended Retail Price"
    COST_PLUS = "cost_plus", "Cost Plus"
    PROMOTIONAL = "promotional", "Promotional"
    SEASONAL = "seasonal", "Seasonal"


class PricingRule(ModelWithMetadata):
    """HoS pricing control rules for products."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    product = models.ForeignKey(
        "product.Product",
        related_name="pricing_rules",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Product this rule applies to (optional)",
    )
    seller = models.ForeignKey(
        Seller,
        related_name="pricing_rules",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Seller this rule applies to (for seller-wide rules)",
    )
    pricing_type = models.CharField(
        max_length=32,
        choices=PricingType.choices,
        help_text="Type of pricing rule",
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Discount percentage (if applicable)",
    )
    fixed_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Fixed price override (if applicable)",
    )
    valid_from = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Start date for seasonal/promotional pricing",
    )
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="End date for seasonal/promotional pricing",
    )
    country = CountryField(
        null=True,
        blank=True,
        help_text="Country this pricing applies to (optional, for country-specific pricing)",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this pricing rule is active"
    )

    class Meta:
        app_label = "marketplace"
        ordering = ("-created_at",)
        indexes = [
            BTreeIndex(fields=["product"], name="pricing_rule_product_idx"),
            BTreeIndex(fields=["seller"], name="pricing_rule_seller_idx"),
            BTreeIndex(fields=["pricing_type"], name="pricing_rule_type_idx"),
            BTreeIndex(fields=["country"], name="pricing_rule_country_idx"),
            BTreeIndex(fields=["is_active"], name="pricing_rule_active_idx"),
            BTreeIndex(fields=["valid_from"], name="pricing_rule_from_idx"),
            BTreeIndex(fields=["valid_until"], name="pricing_rule_until_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(product__isnull=True, seller__isnull=True),
                name="pricing_rule_requires_product_or_seller",
            )
        ]

    def __str__(self):
        target = self.product.name if self.product else self.seller.store_name
        return f"Pricing rule: {target} ({self.pricing_type})"


class PaymentGatewayConfig(ModelWithMetadata):
    """Payment gateway configuration for sellers."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    seller = models.ForeignKey(
        Seller,
        related_name="payment_gateway_configs",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Seller this gateway config applies to (optional, for seller-specific gateways)",
    )
    gateway_name = models.CharField(
        max_length=255, help_text="Payment gateway name (Stripe, PayPal, etc.)"
    )
    gateway_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Gateway-specific configuration settings (JSON)",
    )
    enabled_countries = CountryField(
        multiple=True,
        blank=True,
        help_text="Countries where this gateway is enabled",
    )
    enabled_currencies = models.JSONField(
        default=list,
        blank=True,
        help_text="Currencies this gateway supports (JSON array)",
    )
    compliance_requirements = models.JSONField(
        default=dict,
        blank=True,
        help_text="Compliance requirements (PCI-DSS, etc.) (JSON)",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this gateway configuration is active"
    )

    class Meta:
        app_label = "marketplace"
        ordering = ("seller", "gateway_name")
        indexes = [
            BTreeIndex(fields=["seller"], name="payment_gateway_seller_idx"),
            BTreeIndex(fields=["gateway_name"], name="payment_gateway_name_idx"),
            BTreeIndex(fields=["is_active"], name="payment_gateway_active_idx"),
        ]

    def __str__(self):
        seller_name = self.seller.store_name if self.seller else "Global"
        return f"{self.gateway_name} - {seller_name}"


class SettlementStatus(models.TextChoices):
    """Status choices for seller settlement."""

    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    PAID = "paid", "Paid"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class NewsletterSubscription(ModelWithMetadata):
    """Newsletter subscription for customers."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    email = models.EmailField(db_index=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the subscription is active",
    )
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the subscription was confirmed (double opt-in)",
    )
    unsubscribed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the user unsubscribed",
    )
    source = models.CharField(
        max_length=255,
        blank=True,
        help_text="Source of the subscription (homepage, checkout, etc.)",
    )
    user = models.ForeignKey(
        User,
        related_name="newsletter_subscriptions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Associated user if available",
    )

    class Meta:
        app_label = "marketplace"
        ordering = ("-created_at",)
        indexes = [
            BTreeIndex(fields=["email"], name="newsletter_email_idx"),
            BTreeIndex(fields=["is_active"], name="newsletter_active_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                condition=models.Q(is_active=True),
                name="unique_active_newsletter_email",
            )
        ]

    def __str__(self):
        return f"Newsletter: {self.email} ({'active' if self.is_active else 'inactive'})"


class SellerSettlement(ModelWithMetadata):
    """Represents a settlement/payout for a seller from an order or group of orders."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    seller = models.ForeignKey(
        Seller,
        related_name="settlements",
        on_delete=models.CASCADE,
        help_text="Seller who receives this settlement",
    )
    order = models.ForeignKey(
        "order.Order",
        related_name="seller_settlements",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Order this settlement is for (null for batch settlements)",
    )

    # Financial amounts
    order_total = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        help_text="Total order amount (gross) for this seller's items",
    )
    platform_fee = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        help_text="Platform fee deducted from order total",
    )
    seller_earnings = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        help_text="Amount seller receives (order_total - platform_fee)",
    )
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
        help_text="Currency code for this settlement",
    )

    # Status and payment tracking
    status = models.CharField(
        max_length=32, choices=SettlementStatus.choices, default=SettlementStatus.PENDING
    )
    stripe_transfer_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Stripe Connect transfer ID if payout was made via Stripe",
    )
    payout_reference = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Internal reference for the payout transaction",
    )
    notes = models.TextField(
        blank=True, help_text="Internal notes about this settlement"
    )

    class Meta:
        app_label = "marketplace"
        ordering = ("-created_at", "-id")
        indexes = [
            BTreeIndex(fields=["seller"], name="settlement_seller_idx"),
            BTreeIndex(fields=["status"], name="settlement_status_idx"),
            BTreeIndex(fields=["created_at"], name="settlement_created_at_idx"),
            BTreeIndex(fields=["order"], name="settlement_order_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["seller", "order"],
                condition=models.Q(order__isnull=False),
                name="unique_settlement_per_seller_order",
            )
        ]

    def __str__(self):
        return f"Settlement {self.id} - {self.seller.store_name} - {self.currency} {self.seller_earnings}"

    @property
    def is_paid(self):
        return self.status == SettlementStatus.PAID
