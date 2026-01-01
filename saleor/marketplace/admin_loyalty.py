"""Django admin interface for loyalty models."""

from django.contrib import admin

from .models_loyalty import (
    Badge,
    LoyaltyPointsBalance,
    LoyaltyPointsTransaction,
    Reward,
    RewardRedemption,
    UserBadge,
)


@admin.register(LoyaltyPointsBalance)
class LoyaltyPointsBalanceAdmin(admin.ModelAdmin):
    """Admin interface for LoyaltyPointsBalance model."""

    list_display = [
        "user",
        "balance",
        "lifetime_earned",
        "lifetime_spent",
        "updated_at",
    ]
    list_filter = ["updated_at"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        ("User Information", {
            "fields": ("id", "user")
        }),
        ("Balance Information", {
            "fields": ("balance", "lifetime_earned", "lifetime_spent")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
        ("Metadata", {
            "fields": ("metadata", "private_metadata"),
            "classes": ("collapse",)
        }),
    )


@admin.register(LoyaltyPointsTransaction)
class LoyaltyPointsTransactionAdmin(admin.ModelAdmin):
    """Admin interface for LoyaltyPointsTransaction model."""

    list_display = [
        "user",
        "points",
        "balance_after",
        "transaction_type",
        "created_at",
        "order",
    ]
    list_filter = ["transaction_type", "created_at"]
    search_fields = [
        "user__email",
        "description",
        "order__number",
    ]
    readonly_fields = ["id", "created_at"]
    date_hierarchy = "created_at"
    fieldsets = (
        ("Transaction Information", {
            "fields": ("id", "user", "points", "balance_after", "transaction_type")
        }),
        ("Details", {
            "fields": ("description", "order", "expires_at")
        }),
        ("Timestamp", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    """Admin interface for Badge model."""

    list_display = [
        "name",
        "slug",
        "criteria_type",
        "criteria_value",
        "points_reward",
        "is_active",
        "created_at",
    ]
    list_filter = ["criteria_type", "is_active", "created_at"]
    search_fields = ["name", "slug", "description"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        ("Badge Information", {
            "fields": ("id", "name", "slug", "description", "icon", "is_active")
        }),
        ("Criteria", {
            "fields": ("criteria_type", "criteria_value")
        }),
        ("Reward", {
            "fields": ("points_reward",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    """Admin interface for UserBadge model."""

    list_display = [
        "user",
        "badge",
        "earned_at",
        "order",
    ]
    list_filter = ["earned_at", "badge"]
    search_fields = [
        "user__email",
        "badge__name",
        "order__number",
    ]
    readonly_fields = ["id", "earned_at"]
    date_hierarchy = "earned_at"
    fieldsets = (
        ("Badge Information", {
            "fields": ("id", "user", "badge")
        }),
        ("Earning Details", {
            "fields": ("order", "earned_at")
        }),
    )


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    """Admin interface for Reward model."""

    list_display = [
        "name",
        "slug",
        "reward_type",
        "points_required",
        "reward_value",
        "is_active",
        "quantity_available",
        "quantity_redeemed",
        "created_at",
    ]
    list_filter = ["reward_type", "is_active", "created_at"]
    search_fields = ["name", "slug", "description"]
    readonly_fields = ["id", "created_at", "updated_at", "quantity_redeemed"]
    fieldsets = (
        ("Reward Information", {
            "fields": ("id", "name", "slug", "description", "is_active")
        }),
        ("Reward Details", {
            "fields": (
                "reward_type",
                "points_required",
                "reward_value",
                "product",
            )
        }),
        ("Availability", {
            "fields": ("quantity_available", "quantity_redeemed", "valid_from", "valid_until")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(RewardRedemption)
class RewardRedemptionAdmin(admin.ModelAdmin):
    """Admin interface for RewardRedemption model."""

    list_display = [
        "user",
        "reward",
        "redemption_code",
        "points_spent",
        "is_used",
        "created_at",
        "expires_at",
    ]
    list_filter = ["is_used", "created_at", "expires_at"]
    search_fields = [
        "user__email",
        "reward__name",
        "redemption_code",
    ]
    readonly_fields = ["id", "created_at"]
    date_hierarchy = "created_at"
    fieldsets = (
        ("Redemption Information", {
            "fields": ("id", "user", "reward", "redemption_code", "points_spent")
        }),
        ("Status", {
            "fields": ("is_used", "used_at", "expires_at")
        }),
        ("Timestamp", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )




