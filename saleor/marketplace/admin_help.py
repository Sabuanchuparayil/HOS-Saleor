"""Django admin interface for help center models."""

from django.contrib import admin

from .models_help import (
    ContactSupportTicket,
    ContactSupportTicketMessage,
    HelpArticle,
    HelpArticleView,
    HelpCategory,
)


@admin.register(HelpCategory)
class HelpCategoryAdmin(admin.ModelAdmin):
    """Admin interface for HelpCategory model."""

    list_display = [
        "name",
        "slug",
        "parent",
        "order",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "parent", "created_at"]
    search_fields = ["name", "slug", "description"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        ("Category Information", {
            "fields": ("id", "name", "slug", "description", "icon", "is_active")
        }),
        ("Organization", {
            "fields": ("parent", "order")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(HelpArticle)
class HelpArticleAdmin(admin.ModelAdmin):
    """Admin interface for HelpArticle model."""

    list_display = [
        "title",
        "slug",
        "category",
        "author",
        "order",
        "views_count",
        "is_featured",
        "is_active",
        "published_at",
    ]
    list_filter = ["is_active", "is_featured", "category", "published_at"]
    search_fields = ["title", "slug", "content", "excerpt"]
    readonly_fields = ["id", "created_at", "updated_at", "views_count"]
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("Article Information", {
            "fields": ("id", "title", "slug", "content", "excerpt", "category", "author")
        }),
        ("Display", {
            "fields": ("order", "is_featured", "is_active", "published_at")
        }),
        ("Analytics", {
            "fields": ("views_count",),
            "classes": ("collapse",)
        }),
        ("SEO", {
            "fields": ("meta_title", "meta_description"),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(HelpArticleView)
class HelpArticleViewAdmin(admin.ModelAdmin):
    """Admin interface for HelpArticleView model."""

    list_display = [
        "article",
        "user",
        "ip_address",
        "viewed_at",
    ]
    list_filter = ["viewed_at"]
    search_fields = [
        "article__title",
        "user__email",
        "ip_address",
    ]
    readonly_fields = ["id", "viewed_at"]
    date_hierarchy = "viewed_at"
    fieldsets = (
        ("View Information", {
            "fields": ("id", "article", "user", "ip_address", "user_agent")
        }),
        ("Timestamp", {
            "fields": ("viewed_at",),
            "classes": ("collapse",)
        }),
    )


class ContactSupportTicketMessageInline(admin.TabularInline):
    """Inline admin for ticket messages."""

    model = ContactSupportTicketMessage
    extra = 0
    readonly_fields = ["id", "created_at"]
    fields = ["message", "user", "is_internal", "created_at"]


@admin.register(ContactSupportTicket)
class ContactSupportTicketAdmin(admin.ModelAdmin):
    """Admin interface for ContactSupportTicket model."""

    list_display = [
        "ticket_number",
        "subject",
        "user",
        "email",
        "status",
        "priority",
        "assigned_to",
        "created_at",
    ]
    list_filter = ["status", "priority", "created_at", "category"]
    search_fields = [
        "ticket_number",
        "subject",
        "message",
        "user__email",
        "email",
    ]
    readonly_fields = ["id", "ticket_number", "created_at", "updated_at"]
    date_hierarchy = "created_at"
    inlines = [ContactSupportTicketMessageInline]
    fieldsets = (
        ("Ticket Information", {
            "fields": ("id", "ticket_number", "subject", "message", "category")
        }),
        ("Contact Information", {
            "fields": ("user", "email")
        }),
        ("Status & Assignment", {
            "fields": ("status", "priority", "assigned_to")
        }),
        ("Resolution", {
            "fields": ("resolved_at", "resolved_by"),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Set resolved_by when status changes to resolved."""
        if change and obj.status == "resolved" and not obj.resolved_by:
            obj.resolved_by = request.user
            from django.utils import timezone
            if not obj.resolved_at:
                obj.resolved_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(ContactSupportTicketMessage)
class ContactSupportTicketMessageAdmin(admin.ModelAdmin):
    """Admin interface for ContactSupportTicketMessage model."""

    list_display = [
        "ticket",
        "user",
        "is_internal",
        "created_at",
    ]
    list_filter = ["is_internal", "created_at"]
    search_fields = [
        "ticket__ticket_number",
        "ticket__subject",
        "message",
        "user__email",
    ]
    readonly_fields = ["id", "created_at"]
    date_hierarchy = "created_at"
    fieldsets = (
        ("Message Information", {
            "fields": ("id", "ticket", "message", "user", "is_internal")
        }),
        ("Timestamp", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )




