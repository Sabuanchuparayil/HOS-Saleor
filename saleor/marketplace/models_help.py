"""Help center models for marketplace."""

from uuid import uuid4

from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.utils import timezone

from ..account.models import User
from ..core.models import ModelWithMetadata


class HelpCategory(models.Model):
    """Category for help articles."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=255, help_text="Category name")
    slug = models.SlugField(
        max_length=255, unique=True, help_text="Unique slug for the category"
    )
    description = models.TextField(
        blank=True, help_text="Category description"
    )
    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="Icon name/class for the category (e.g., 'faq', 'shipping')",
    )
    parent = models.ForeignKey(
        "self",
        related_name="children",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Parent category for nested categories",
    )
    order = models.IntegerField(
        default=0, help_text="Display order (lower numbers appear first)"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this category is currently active"
    )

    class Meta:
        ordering = ("order", "name")
        verbose_name_plural = "Help categories"
        indexes = [
            models.Index(fields=["slug"], name="help_category_slug_idx"),
            models.Index(fields=["parent", "order"], name="help_category_parent_order_idx"),
        ]

    def __str__(self):
        return self.name


class HelpArticle(models.Model):
    """Help article/documentation."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(
        null=True, blank=True, help_text="When this article was published"
    )

    title = models.CharField(max_length=255, help_text="Article title")
    slug = models.SlugField(
        max_length=255, unique=True, help_text="Unique slug for the article"
    )
    content = models.TextField(help_text="Article content (Markdown or HTML)")
    excerpt = models.TextField(
        blank=True, help_text="Short excerpt/summary of the article"
    )
    category = models.ForeignKey(
        HelpCategory,
        related_name="articles",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Category this article belongs to",
    )
    author = models.ForeignKey(
        User,
        related_name="help_articles",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who created/updated this article",
    )
    order = models.IntegerField(
        default=0, help_text="Display order within category (lower numbers appear first)"
    )
    views_count = models.IntegerField(
        default=0, help_text="Number of times this article has been viewed"
    )
    is_featured = models.BooleanField(
        default=False, help_text="Whether to feature this article"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this article is currently active"
    )
    meta_title = models.CharField(
        max_length=255, blank=True, help_text="SEO meta title"
    )
    meta_description = models.TextField(
        blank=True, help_text="SEO meta description"
    )

    class Meta:
        ordering = ("order", "title")
        indexes = [
            models.Index(fields=["slug"], name="help_article_slug_idx"),
            models.Index(fields=["category", "order"], name="help_article_cat_order_idx"),
            models.Index(fields=["is_active", "is_featured"], name="help_article_active_feat_idx"),
            GinIndex(
                fields=["title", "content"],
                name="help_article_search_gin",
                opclasses=["gin_trgm_ops", "gin_trgm_ops"],
            ),
        ]

    def __str__(self):
        return self.title

    def increment_views(self):
        """Increment the view count."""
        self.views_count = models.F("views_count") + 1
        self.save(update_fields=["views_count"])


class HelpArticleView(models.Model):
    """Track views of help articles (for analytics)."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    viewed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    article = models.ForeignKey(
        HelpArticle,
        related_name="article_views",
        on_delete=models.CASCADE,
        help_text="Article that was viewed",
    )
    user = models.ForeignKey(
        User,
        related_name="help_article_views",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who viewed the article (null for anonymous)",
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, help_text="IP address of the viewer"
    )
    user_agent = models.TextField(
        blank=True, help_text="User agent string"
    )

    class Meta:
        ordering = ("-viewed_at",)
        indexes = [
            models.Index(fields=["article"], name="help_article_view_article_idx"),
            models.Index(fields=["viewed_at"], name="help_article_view_date_idx"),
        ]

    def __str__(self):
        return f"{self.article.title} - {self.viewed_at}"


class ContactSupportTicket(models.Model):
    """Support ticket/contact form submission."""

    TICKET_STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    TICKET_PRIORITY_CHOICES = [
        ("low", "Low"),
        ("normal", "Normal"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    ticket_number = models.CharField(
        max_length=50, unique=True, help_text="Unique ticket number"
    )
    subject = models.CharField(max_length=255, help_text="Ticket subject")
    message = models.TextField(help_text="Ticket message/content")
    category = models.ForeignKey(
        HelpCategory,
        related_name="support_tickets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Category this ticket belongs to",
    )
    user = models.ForeignKey(
        User,
        related_name="support_tickets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who created this ticket (null for guest)",
    )
    email = models.EmailField(
        help_text="Email address for contact (required for guest tickets)"
    )
    status = models.CharField(
        max_length=32,
        choices=TICKET_STATUS_CHOICES,
        default="open",
        help_text="Current status of the ticket",
    )
    priority = models.CharField(
        max_length=32,
        choices=TICKET_PRIORITY_CHOICES,
        default="normal",
        help_text="Priority level of the ticket",
    )
    assigned_to = models.ForeignKey(
        User,
        related_name="assigned_support_tickets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Staff member assigned to handle this ticket",
    )
    resolved_at = models.DateTimeField(
        null=True, blank=True, help_text="When the ticket was resolved"
    )
    resolved_by = models.ForeignKey(
        User,
        related_name="resolved_support_tickets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Staff member who resolved this ticket",
    )

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["ticket_number"], name="support_ticket_number_idx"),
            models.Index(fields=["status", "priority"], name="support_ticket_stat_pri_idx"),
            models.Index(fields=["user"], name="support_ticket_user_idx"),
            models.Index(fields=["assigned_to"], name="support_ticket_assigned_idx"),
        ]

    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"

    def save(self, *args, **kwargs):
        """Generate ticket number if not set."""
        if not self.ticket_number:
            import random
            import string
            self.ticket_number = "TKT-" + "".join(
                random.choices(string.ascii_uppercase + string.digits, k=10)
            )
        super().save(*args, **kwargs)


class ContactSupportTicketMessage(models.Model):
    """Message/reply in a support ticket thread."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    ticket = models.ForeignKey(
        ContactSupportTicket,
        related_name="messages",
        on_delete=models.CASCADE,
        help_text="Ticket this message belongs to",
    )
    message = models.TextField(help_text="Message content")
    user = models.ForeignKey(
        User,
        related_name="support_ticket_messages",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who sent this message (null for system messages)",
    )
    is_internal = models.BooleanField(
        default=False, help_text="Whether this is an internal note (not visible to customer)"
    )

    class Meta:
        ordering = ("created_at",)
        indexes = [
            models.Index(fields=["ticket"], name="support_ticket_msg_ticket_idx"),
            models.Index(fields=["created_at"], name="support_ticket_msg_date_idx"),
        ]

    def __str__(self):
        return f"{self.ticket.ticket_number} - Message {self.id}"

