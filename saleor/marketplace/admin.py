"""Django admin interface for marketplace models."""

from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Badge,
    ContactSupportTicket,
    ContactSupportTicketMessage,
    FandomCharacter,
    FulfillmentCenter,
    HelpArticle,
    HelpArticleView,
    HelpCategory,
    InventorySync,
    NewsletterSubscription,
    OrderRoutingRule,
    PaymentGatewayConfig,
    PricingRule,
    ProductSubmission,
    ReturnPolicy,
    ReturnRequest,
    Reward,
    RewardRedemption,
    Seller,
    SellerDomain,
    SellerLogisticsConfig,
    SellerSettlement,
    SellerShippingMethod,
    SellerStorefrontSettings,
    SellerTaxRegistration,
    SellerWarehouse,
    Theme,
    ThemeVersion,
    UserBadge,
)
from .models_discount import SellerDiscountConfig
from .models_loyalty import (
    LoyaltyPointsBalance,
    LoyaltyPointsTransaction,
)


class SellerLogisticsConfigInline(admin.StackedInline):
    """Inline editor for a seller's one-to-one logistics configuration."""

    model = SellerLogisticsConfig
    fk_name = "seller"
    can_delete = False
    extra = 0
    autocomplete_fields = ["primary_fulfillment_center"]
    filter_horizontal = ["shipping_zones"]
    fieldsets = (
        (
            "Fulfillment",
            {
                "fields": (
                    "fulfillment_method",
                    "primary_fulfillment_center",
                    "handling_time_days",
                )
            },
        ),
        (
            "Shipping",
            {
                "fields": (
                    "shipping_provider",
                    "free_shipping_threshold",
                    "shipping_zones",
                    "custom_shipping_methods",
                )
            },
        ),
        ("Integration", {"fields": ("logistics_partner_integration",)}),
    )


class SellerDomainInline(admin.TabularInline):
    """Inline list of domains for a seller."""

    model = SellerDomain
    extra = 0
    fields = ("domain", "is_primary", "status", "ssl_enabled", "verified_at")
    readonly_fields = ("verified_at",)


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    """Admin interface for Seller model."""

    list_display = [
        "store_name",
        "slug",
        "status",
        "seller_type",
        "is_authorized_distributor",
        "owner",
        "platform_fee_percentage",
        "created_at",
    ]
    list_filter = [
        "status",
        "seller_type",
        "is_authorized_distributor",
        "distributor_category",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "store_name",
        "slug",
        "owner__email",
        "owner__first_name",
        "owner__last_name",
        "business_registration_number",
    ]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "store_name",
                    "slug",
                    "description",
                    "logo",
                    "status",
                )
            },
        ),
        (
            "Business Model",
            {
                "fields": (
                    "seller_type",
                    "is_authorized_distributor",
                    "distributor_category",
                    "minimum_order_quantity",
                    "credit_terms_enabled",
                    "business_registration_number",
                )
            },
        ),
        ("Owner & Staff", {"fields": ("owner", "staff")}),
        ("Financial", {"fields": ("platform_fee_percentage", "stripe_account_id")}),
        ("Tax & Shipping", {"fields": ("tax_origin_address", "channel")}),
        ("Metadata", {"fields": ("metadata", "private_metadata")}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    filter_horizontal = ["staff"]
    autocomplete_fields = ["owner", "tax_origin_address", "channel"]
    inlines = [SellerLogisticsConfigInline, SellerDomainInline]


@admin.register(SellerDomain)
class SellerDomainAdmin(admin.ModelAdmin):
    """Admin interface for SellerDomain model."""

    list_display = ["domain", "seller", "is_primary", "status", "ssl_enabled", "verified_at"]
    list_filter = ["status", "is_primary", "ssl_enabled", "verified_at"]
    search_fields = ["domain", "seller__store_name"]
    readonly_fields = ["id", "created_at", "updated_at", "verified_at"]
    fieldsets = (
        ("Domain Information", {"fields": ("seller", "domain", "is_primary")}),
        ("Status", {"fields": ("status", "ssl_enabled", "verified_at")}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["seller"]


@admin.register(SellerStorefrontSettings)
class SellerStorefrontSettingsAdmin(admin.ModelAdmin):
    """Admin interface for SellerStorefrontSettings model."""

    list_display = ["seller", "theme", "primary_color", "secondary_color", "updated_at"]
    list_filter = ["theme", "updated_at"]
    search_fields = ["seller__store_name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        ("Seller", {"fields": ("seller",)}),
        ("Theme", {"fields": ("theme", "theme_customizations")}),
        ("Branding", {"fields": ("primary_color", "secondary_color", "favicon", "storefront_logo", "custom_css")}),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
        ("Social Media", {"fields": ("facebook_url", "twitter_url", "instagram_url")}),
        ("Contact", {"fields": ("contact_email", "contact_phone")}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["seller", "theme"]


@admin.register(SellerTaxRegistration)
class SellerTaxRegistrationAdmin(admin.ModelAdmin):
    """Admin interface for SellerTaxRegistration model."""

    list_display = ["seller", "country", "registration_type", "registration_number", "is_active", "created_at"]
    list_filter = ["registration_type", "is_active", "country", "created_at"]
    search_fields = ["seller__store_name", "registration_number", "country"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        ("Registration Information", {"fields": ("seller", "country", "registration_type", "registration_number")}),
        ("Status", {"fields": ("is_active",)}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["seller"]


@admin.register(SellerWarehouse)
class SellerWarehouseAdmin(admin.ModelAdmin):
    """Admin interface for SellerWarehouse model."""

    list_display = ["seller", "warehouse", "is_primary", "priority", "created_at"]
    list_filter = ["is_primary", "priority", "created_at"]
    search_fields = ["seller__store_name", "warehouse__name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        ("Assignment", {"fields": ("seller", "warehouse", "is_primary", "priority")}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["seller", "warehouse"]


@admin.register(SellerSettlement)
class SellerSettlementAdmin(admin.ModelAdmin):
    """Admin interface for SellerSettlement model."""

    list_display = [
        "seller",
        "order",
        "order_total",
        "platform_fee",
        "seller_earnings",
        "status",
        "created_at",
    ]
    list_filter = ["status", "currency", "created_at", "paid_at"]
    search_fields = ["seller__store_name", "order__number", "payout_reference"]
    readonly_fields = ["id", "created_at", "updated_at", "paid_at"]
    fieldsets = (
        ("Settlement Information", {"fields": ("seller", "order", "currency")}),
        ("Financial Details", {"fields": ("order_total", "platform_fee", "seller_earnings")}),
        ("Status", {"fields": ("status", "stripe_transfer_id", "payout_reference", "paid_at")}),
        ("Notes", {"fields": ("notes",)}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["seller", "order"]


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    """Admin interface for Theme model."""

    list_display = ["name", "slug", "is_default", "is_active", "created_at"]
    list_filter = ["is_default", "is_active", "created_at"]
    search_fields = ["name", "slug", "description"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        ("Theme Information", {"fields": ("name", "slug", "description", "is_default", "is_active")}),
        ("Template Data", {"fields": ("template_data", "preview_image")}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )


@admin.register(ThemeVersion)
class ThemeVersionAdmin(admin.ModelAdmin):
    """Admin interface for ThemeVersion model."""

    list_display = ["theme", "version_number", "created_at"]
    list_filter = ["theme", "created_at"]
    search_fields = ["theme__name", "notes"]
    readonly_fields = ["id", "created_at"]
    fieldsets = (
        ("Version Information", {"fields": ("theme", "version_number", "notes")}),
        ("Template Data", {"fields": ("template_data",)}),
        ("Timestamps", {"fields": ("id", "created_at")}),
    )
    autocomplete_fields = ["theme"]


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for NewsletterSubscription model."""

    list_display = ["email", "user", "is_active", "confirmed_at", "created_at"]
    list_filter = ["is_active", "source", "confirmed_at", "created_at"]
    search_fields = ["email", "user__email"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        ("Subscription Information", {"fields": ("email", "user", "is_active", "source")}),
        ("Status", {"fields": ("confirmed_at", "unsubscribed_at")}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["user"]


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    """Admin interface for Badge model."""

    list_display = ["name", "slug", "criteria_type", "points_reward", "is_active", "created_at"]
    list_filter = ["criteria_type", "is_active", "created_at"]
    search_fields = ["name", "slug", "description"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        ("Badge Information", {"fields": ("name", "slug", "description", "icon", "is_active")}),
        ("Criteria", {"fields": ("criteria_type", "criteria_value", "points_reward")}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    """Admin interface for UserBadge model."""

    list_display = ["user", "badge", "earned_at", "order"]
    list_filter = ["badge", "earned_at"]
    search_fields = ["user__email", "badge__name", "order__number"]
    readonly_fields = ["id", "earned_at"]
    fieldsets = (
        ("Badge Assignment", {"fields": ("user", "badge", "order")}),
        ("Timestamps", {"fields": ("id", "earned_at")}),
    )
    autocomplete_fields = ["user", "badge", "order"]


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    """Admin interface for Reward model."""

    list_display = ["name", "slug", "points_required", "reward_type", "is_active", "is_available", "created_at"]
    list_filter = ["reward_type", "is_active", "is_available", "created_at"]
    search_fields = ["name", "slug", "description"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        ("Reward Information", {"fields": ("name", "slug", "description", "icon", "is_active", "is_available")}),
        ("Redemption", {"fields": ("points_required", "reward_type", "reward_value", "product")}),
        ("Availability", {"fields": ("quantity_available", "quantity_redeemed", "valid_from", "valid_until")}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["product"]


@admin.register(RewardRedemption)
class RewardRedemptionAdmin(admin.ModelAdmin):
    """Admin interface for RewardRedemption model."""

    list_display = ["user", "reward", "points_used", "used_at", "expires_at"]
    list_filter = ["reward", "used_at", "expires_at"]
    search_fields = ["user__email", "reward__name"]
    readonly_fields = ["id", "used_at"]
    fieldsets = (
        ("Redemption Information", {"fields": ("user", "reward", "points_used")}),
        ("Status", {"fields": ("used_at", "expires_at")}),
        ("Timestamps", {"fields": ("id", "used_at")}),
    )
    autocomplete_fields = ["user", "reward"]


@admin.register(HelpCategory)
class HelpCategoryAdmin(admin.ModelAdmin):
    """Admin interface for HelpCategory model."""

    list_display = ["name", "slug", "parent", "order", "is_active", "created_at"]
    list_filter = ["is_active", "parent", "created_at"]
    search_fields = ["name", "slug", "description"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        ("Category Information", {"fields": ("name", "slug", "description", "icon", "parent", "order", "is_active")}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["parent"]


@admin.register(HelpArticle)
class HelpArticleAdmin(admin.ModelAdmin):
    """Admin interface for HelpArticle model."""

    list_display = ["title", "category", "author", "order", "is_featured", "is_active", "views_count", "created_at"]
    list_filter = ["category", "is_featured", "is_active", "published_at", "created_at"]
    search_fields = ["title", "slug", "content", "excerpt"]
    readonly_fields = ["id", "views_count", "created_at", "updated_at"]
    fieldsets = (
        ("Article Information", {"fields": ("title", "slug", "category", "author", "order")}),
        ("Content", {"fields": ("content", "excerpt")}),
        ("Status", {"fields": ("is_featured", "is_active", "published_at", "views_count")}),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["category", "author"]


@admin.register(HelpArticleView)
class HelpArticleViewAdmin(admin.ModelAdmin):
    """Admin interface for HelpArticleView model."""

    list_display = ["article", "user", "viewed_at", "ip_address"]
    list_filter = ["viewed_at"]
    search_fields = ["article__title", "user__email", "ip_address"]
    readonly_fields = ["id", "viewed_at"]
    fieldsets = (
        ("View Information", {"fields": ("article", "user", "ip_address", "user_agent")}),
        ("Timestamps", {"fields": ("id", "viewed_at")}),
    )
    autocomplete_fields = ["article", "user"]


@admin.register(FandomCharacter)
class FandomCharacterAdmin(admin.ModelAdmin):
    """Admin interface for FandomCharacter model."""

    list_display = ["name", "slug", "fandom_universe", "featured", "is_active", "created_at"]
    list_filter = ["fandom_universe", "featured", "is_active", "created_at"]
    search_fields = ["name", "slug", "description", "fandom_universe"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        ("Character Information", {"fields": ("name", "slug", "fandom_universe", "description", "image", "featured", "is_active")}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin interface for Quiz model."""

    list_display = ["title", "slug", "character", "collection", "points_reward", "featured", "is_active", "created_at"]
    list_filter = ["character", "collection", "featured", "is_active", "created_at"]
    search_fields = ["title", "slug", "description"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        ("Quiz Information", {"fields": ("title", "slug", "description", "featured", "is_active")}),
        ("Relations", {"fields": ("character", "collection")}),
        ("Rewards", {"fields": ("points_reward",)}),
        ("Questions", {"fields": ("questions",)}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["character", "collection"]


@admin.register(ContactSupportTicket)
class ContactSupportTicketAdmin(admin.ModelAdmin):
    """Admin interface for ContactSupportTicket model."""

    list_display = ["ticket_number", "subject", "user", "email", "status", "priority", "assigned_to", "created_at"]
    list_filter = ["status", "priority", "category", "created_at", "resolved_at"]
    search_fields = ["ticket_number", "subject", "message", "user__email", "email"]
    readonly_fields = ["id", "ticket_number", "created_at", "updated_at", "resolved_at"]
    fieldsets = (
        ("Ticket Information", {"fields": ("ticket_number", "subject", "message", "category")}),
        ("Contact", {"fields": ("user", "email")}),
        ("Status", {"fields": ("status", "priority", "assigned_to")}),
        ("Resolution", {"fields": ("resolved_at", "resolved_by")}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["user", "category", "assigned_to", "resolved_by"]


@admin.register(ContactSupportTicketMessage)
class ContactSupportTicketMessageAdmin(admin.ModelAdmin):
    """Admin interface for ContactSupportTicketMessage model."""

    list_display = ["ticket", "user", "is_internal", "created_at"]
    list_filter = ["is_internal", "created_at"]
    search_fields = ["ticket__ticket_number", "ticket__subject", "message", "user__email"]
    readonly_fields = ["id", "created_at"]
    fieldsets = (
        ("Message Information", {"fields": ("ticket", "user", "message", "is_internal")}),
        ("Timestamps", {"fields": ("id", "created_at")}),
    )
    autocomplete_fields = ["ticket", "user"]


@admin.register(ProductCharacter)
class ProductCharacterAdmin(admin.ModelAdmin):
    """Admin interface for ProductCharacter model."""

    list_display = ["product", "character", "is_primary", "created_at"]
    list_filter = ["is_primary", "created_at"]
    search_fields = ["product__name", "character__name"]
    readonly_fields = ["id", "created_at"]
    fieldsets = (
        ("Association", {"fields": ("product", "character", "is_primary")}),
        ("Timestamps", {"fields": ("id", "created_at")}),
    )
    autocomplete_fields = ["product", "character"]


@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    """Admin interface for QuizSubmission model."""

    list_display = ["quiz", "user", "score", "points_awarded", "completed_at"]
    list_filter = ["quiz", "completed_at"]
    search_fields = ["quiz__title", "user__email"]
    readonly_fields = ["id", "created_at", "completed_at"]
    fieldsets = (
        ("Submission Information", {"fields": ("quiz", "user", "answers", "score", "points_awarded")}),
        ("Timestamps", {"fields": ("id", "created_at", "completed_at")}),
    )
    autocomplete_fields = ["quiz", "user"]


@admin.register(FulfillmentCenter)
class FulfillmentCenterAdmin(admin.ModelAdmin):
    """Admin interface for FulfillmentCenter model."""

    list_display = ["name", "location", "country", "is_active", "priority", "created_at"]
    list_filter = ["country", "is_active", "created_at"]
    search_fields = ["name", "location"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        ("Center Information", {"fields": ("name", "location", "country", "address")}),
        ("Status", {"fields": ("is_active", "priority")}),
        ("Warehouses", {"fields": ("warehouses",)}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    filter_horizontal = ["warehouses"]
    autocomplete_fields = ["address"]


@admin.register(SellerLogisticsConfig)
class SellerLogisticsConfigAdmin(admin.ModelAdmin):
    """Admin interface for SellerLogisticsConfig model."""

    list_display = [
        "seller",
        "fulfillment_method",
        "primary_fulfillment_center",
        "handling_time_days",
        "free_shipping_threshold",
        "created_at",
    ]
    list_filter = ["fulfillment_method", "created_at"]
    search_fields = ["seller__store_name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        ("Seller", {"fields": ("seller",)}),
        (
            "Fulfillment",
            {
                "fields": (
                    "fulfillment_method",
                    "primary_fulfillment_center",
                    "handling_time_days",
                )
            },
        ),
        (
            "Shipping",
            {
                "fields": (
                    "shipping_provider",
                    "free_shipping_threshold",
                    "shipping_zones",
                    "custom_shipping_methods",
                )
            },
        ),
        (
            "Integration",
            {"fields": ("logistics_partner_integration",)},
        ),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["seller", "primary_fulfillment_center"]
    filter_horizontal = ["shipping_zones"]


@admin.register(SellerShippingMethod)
class SellerShippingMethodAdmin(admin.ModelAdmin):
    """Admin interface for SellerShippingMethod model."""

    list_display = [
        "name",
        "seller",
        "price",
        "estimated_days",
        "fulfillment_center",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "fulfillment_center", "created_at"]
    search_fields = ["name", "seller__store_name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        (
            "Method Information",
            {
                "fields": (
                    "seller",
                    "name",
                    "price",
                    "estimated_days",
                    "is_active",
                )
            },
        ),
        (
            "Routing",
            {
                "fields": (
                    "fulfillment_center",
                    "destination_country",
                    "destination_city",
                )
            },
        ),
        ("Tiered Pricing", {"fields": ("tiered_pricing",)}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["seller", "fulfillment_center"]


@admin.register(OrderRoutingRule)
class OrderRoutingRuleAdmin(admin.ModelAdmin):
    """Admin interface for OrderRoutingRule model."""

    list_display = ["name", "fulfillment_center", "priority", "is_active", "created_at"]
    list_filter = ["fulfillment_center", "is_active", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        ("Rule Information", {"fields": ("name", "fulfillment_center", "priority", "is_active")}),
        ("Conditions", {"fields": ("conditions",)}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["fulfillment_center"]


@admin.register(SellerDiscountConfig)
class SellerDiscountConfigAdmin(admin.ModelAdmin):
    """Admin interface for SellerDiscountConfig model."""

    list_display = [
        "seller",
        "max_discount_percentage",
        "min_order_value_for_discount",
        "allow_sku_level_discounts",
        "allow_category_level_discounts",
        "allow_seller_level_discounts",
        "created_at",
    ]
    list_filter = [
        "allow_sku_level_discounts",
        "allow_category_level_discounts",
        "allow_seller_level_discounts",
        "created_at",
    ]
    search_fields = ["seller__store_name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        ("Seller", {"fields": ("seller",)}),
        (
            "Discount Limits",
            {
                "fields": (
                    "max_discount_percentage",
                    "min_order_value_for_discount",
                )
            },
        ),
        (
            "Discount Permissions",
            {
                "fields": (
                    "allow_sku_level_discounts",
                    "allow_category_level_discounts",
                    "allow_seller_level_discounts",
                )
            },
        ),
        ("Rules", {"fields": ("discount_rules",)}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["seller"]


@admin.register(ProductSubmission)
class ProductSubmissionAdmin(admin.ModelAdmin):
    """Admin interface for ProductSubmission model."""

    list_display = [
        "product",
        "seller",
        "status",
        "submitted_at",
        "reviewed_by",
        "reviewed_at",
    ]
    list_filter = ["status", "submitted_at", "reviewed_at"]
    search_fields = ["product__name", "seller__store_name", "admin_notes"]
    readonly_fields = ["id", "submitted_at", "created_at", "updated_at"]
    fieldsets = (
        (
            "Submission Information",
            {"fields": ("seller", "product", "status", "submitted_at")},
        ),
        (
            "Review",
            {"fields": ("admin_notes", "reviewed_by", "reviewed_at")},
        ),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["seller", "product", "reviewed_by"]


@admin.register(ReturnPolicy)
class ReturnPolicyAdmin(admin.ModelAdmin):
    """Admin interface for ReturnPolicy model."""

    list_display = [
        "seller",
        "product",
        "return_period_days",
        "return_shipping_cost",
        "is_active",
        "created_at",
    ]
    list_filter = ["return_shipping_cost", "is_active", "created_at"]
    search_fields = ["seller__store_name", "product__name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        (
            "Policy Scope",
            {"fields": ("seller", "product")},
        ),
        (
            "Policy Details",
            {
                "fields": (
                    "return_period_days",
                    "return_conditions",
                    "return_shipping_cost",
                    "is_active",
                )
            },
        ),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["seller", "product"]


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    """Admin interface for ReturnRequest model."""

    list_display = [
        "order",
        "order_line",
        "user",
        "status",
        "requested_at",
        "processed_at",
        "processed_by",
    ]
    list_filter = ["status", "requested_at", "processed_at"]
    search_fields = ["order__number", "user__email", "reason"]
    readonly_fields = ["id", "requested_at", "created_at", "updated_at"]
    fieldsets = (
        (
            "Return Information",
            {"fields": ("order", "order_line", "user", "reason", "status")},
        ),
        (
            "Processing",
            {"fields": ("processed_at", "processed_by")},
        ),
        ("Timestamps", {"fields": ("id", "requested_at", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["order", "order_line", "user", "processed_by"]


@admin.register(InventorySync)
class InventorySyncAdmin(admin.ModelAdmin):
    """Admin interface for InventorySync model."""

    list_display = [
        "product_variant",
        "fulfillment_center",
        "warehouse",
        "quantity_available",
        "quantity_reserved",
        "sync_method",
        "synced_at",
    ]
    list_filter = ["fulfillment_center", "sync_method", "synced_at"]
    search_fields = ["product_variant__sku", "product_variant__name"]
    readonly_fields = ["id", "synced_at", "created_at", "updated_at"]
    fieldsets = (
        (
            "Sync Information",
            {
                "fields": (
                    "product_variant",
                    "fulfillment_center",
                    "warehouse",
                    "sync_method",
                )
            },
        ),
        (
            "Inventory",
            {"fields": ("quantity_available", "quantity_reserved")},
        ),
        ("Timestamps", {"fields": ("id", "synced_at", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["product_variant", "fulfillment_center", "warehouse"]


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    """Admin interface for PricingRule model."""

    list_display = [
        "product",
        "seller",
        "pricing_type",
        "discount_percentage",
        "fixed_price",
        "country",
        "is_active",
        "valid_from",
        "valid_until",
    ]
    list_filter = ["pricing_type", "country", "is_active", "created_at"]
    search_fields = ["product__name", "seller__store_name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        (
            "Rule Scope",
            {"fields": ("product", "seller", "country")},
        ),
        (
            "Pricing",
            {
                "fields": (
                    "pricing_type",
                    "discount_percentage",
                    "fixed_price",
                    "is_active",
                )
            },
        ),
        (
            "Validity",
            {"fields": ("valid_from", "valid_until")},
        ),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["product", "seller"]


@admin.register(PaymentGatewayConfig)
class PaymentGatewayConfigAdmin(admin.ModelAdmin):
    """Admin interface for PaymentGatewayConfig model."""

    list_display = [
        "gateway_name",
        "seller",
        "is_active",
        "created_at",
    ]
    list_filter = ["gateway_name", "is_active", "created_at"]
    search_fields = ["gateway_name", "seller__store_name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        (
            "Configuration",
            {
                "fields": (
                    "seller",
                    "gateway_name",
                    "gateway_config",
                    "is_active",
                )
            },
        ),
        (
            "Scope",
            {"fields": ("enabled_countries", "enabled_currencies", "compliance_requirements")},
        ),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )
    autocomplete_fields = ["seller"]
