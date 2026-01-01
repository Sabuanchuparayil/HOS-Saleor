"""Loyalty system models for marketplace."""

from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.contrib.postgres.indexes import BTreeIndex
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from ..account.models import User
from ..core.models import ModelWithMetadata
from ..product.models import Product


class LoyaltyPointsTransaction(models.Model):
    """Record of a loyalty points transaction (earned or spent)."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    user = models.ForeignKey(
        User,
        related_name="loyalty_points_transactions",
        on_delete=models.CASCADE,
        help_text="User who earned or spent the points",
    )
    points = models.IntegerField(
        help_text="Number of points (positive for earned, negative for spent)"
    )
    balance_after = models.IntegerField(
        help_text="User's balance after this transaction"
    )
    transaction_type = models.CharField(
        max_length=32,
        choices=[
            ("earned", "Earned"),
            ("spent", "Spent"),
            ("expired", "Expired"),
            ("adjusted", "Adjusted"),
        ],
        help_text="Type of transaction",
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the transaction (e.g., 'Points from order #123')",
    )
    order = models.ForeignKey(
        "order.Order",
        related_name="loyalty_points_transactions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Order that triggered this transaction (if applicable)",
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When these points expire (if applicable)",
    )

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            BTreeIndex(fields=["user"], name="loyalty_tx_user_idx"),
            BTreeIndex(fields=["created_at"], name="loyalty_tx_created_idx"),
            BTreeIndex(fields=["transaction_type"], name="loyalty_tx_type_idx"),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.transaction_type} {abs(self.points)} points"


class LoyaltyPointsBalance(ModelWithMetadata):
    """Current loyalty points balance for a user."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.OneToOneField(
        User,
        related_name="loyalty_points_balance",
        on_delete=models.CASCADE,
        help_text="User who owns this balance",
    )
    balance = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Current points balance",
    )
    lifetime_earned = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total points ever earned (for tracking)",
    )
    lifetime_spent = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total points ever spent (for tracking)",
    )

    class Meta:
        indexes = [
            BTreeIndex(fields=["user"], name="loyalty_balance_user_idx"),
            BTreeIndex(fields=["balance"], name="loyalty_balance_balance_idx"),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.balance} points"

    def add_points(self, points: int, description: str = "", order=None, expires_at=None):
        """Add points to the balance and create a transaction record."""
        if points <= 0:
            raise ValueError("Points must be positive")
        
        from .utils_loyalty import create_points_transaction
        
        self.balance += points
        self.lifetime_earned += points
        self.save(update_fields=["balance", "lifetime_earned", "updated_at"])
        
        create_points_transaction(
            user=self.user,
            points=points,
            transaction_type="earned",
            description=description,
            order=order,
            expires_at=expires_at,
        )

    def spend_points(self, points: int, description: str = ""):
        """Spend points from the balance and create a transaction record."""
        if points <= 0:
            raise ValueError("Points must be positive")
        if self.balance < points:
            raise ValueError("Insufficient points balance")
        
        from .utils_loyalty import create_points_transaction
        
        self.balance -= points
        self.lifetime_spent += points
        self.save(update_fields=["balance", "lifetime_spent", "updated_at"])
        
        create_points_transaction(
            user=self.user,
            points=-points,
            transaction_type="spent",
            description=description,
        )


class Badge(models.Model):
    """Definition of a badge that users can earn."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=255, help_text="Name of the badge")
    slug = models.SlugField(
        max_length=255, unique=True, help_text="Unique slug for the badge"
    )
    description = models.TextField(
        blank=True, help_text="Description of what the badge represents"
    )
    icon = models.ImageField(
        upload_to="badge-icons", blank=True, null=True, help_text="Badge icon/image"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this badge is currently active"
    )
    criteria_type = models.CharField(
        max_length=32,
        choices=[
            ("order_count", "Order Count"),
            ("total_spent", "Total Spent"),
            ("loyalty_points", "Loyalty Points"),
            ("manual", "Manual Assignment"),
        ],
        help_text="Type of criteria for earning this badge",
    )
    criteria_value = models.IntegerField(
        null=True,
        blank=True,
        help_text="Value required to earn this badge (e.g., 10 orders, 1000 points)",
    )
    points_reward = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Points awarded when this badge is earned",
    )

    class Meta:
        ordering = ("name",)
        indexes = [
            BTreeIndex(fields=["slug"], name="badge_slug_idx"),
            BTreeIndex(fields=["is_active"], name="badge_active_idx"),
        ]

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    """Record of a badge earned by a user."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    user = models.ForeignKey(
        User,
        related_name="badges",
        on_delete=models.CASCADE,
        help_text="User who earned the badge",
    )
    badge = models.ForeignKey(
        Badge,
        related_name="user_badges",
        on_delete=models.CASCADE,
        help_text="Badge that was earned",
    )
    earned_at = models.DateTimeField(
        auto_now_add=True, help_text="When the badge was earned"
    )
    order = models.ForeignKey(
        "order.Order",
        related_name="badges_earned",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Order that triggered this badge (if applicable)",
    )

    class Meta:
        ordering = ("-earned_at",)
        unique_together = [("user", "badge")]
        indexes = [
            BTreeIndex(fields=["user"], name="user_badge_user_idx"),
            BTreeIndex(fields=["badge"], name="user_badge_badge_idx"),
            BTreeIndex(fields=["earned_at"], name="user_badge_earned_idx"),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.badge.name}"


class Reward(models.Model):
    """Definition of a reward that can be redeemed with loyalty points."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=255, help_text="Name of the reward")
    slug = models.SlugField(
        max_length=255, unique=True, help_text="Unique slug for the reward"
    )
    description = models.TextField(
        blank=True, help_text="Description of the reward"
    )
    points_required = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Points required to redeem this reward",
    )
    reward_type = models.CharField(
        max_length=32,
        choices=[
            ("discount", "Discount Code"),
            ("product", "Free Product"),
            ("voucher", "Gift Voucher"),
            ("shipping", "Free Shipping"),
        ],
        help_text="Type of reward",
    )
    reward_value = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        null=True,
        blank=True,
        help_text="Value of the reward (e.g., discount amount, voucher amount)",
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    product = models.ForeignKey(
        Product,
        related_name="reward_products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Product for free product rewards",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this reward is currently available"
    )
    quantity_available = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of times this reward can be redeemed (null = unlimited)",
        validators=[MinValueValidator(0)],
    )
    quantity_redeemed = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of times this reward has been redeemed",
    )
    valid_from = models.DateTimeField(
        null=True, blank=True, help_text="When this reward becomes available"
    )
    valid_until = models.DateTimeField(
        null=True, blank=True, help_text="When this reward expires"
    )

    class Meta:
        ordering = ("points_required", "name")
        indexes = [
            BTreeIndex(fields=["slug"], name="reward_slug_idx"),
            BTreeIndex(fields=["is_active"], name="reward_active_idx"),
            BTreeIndex(fields=["points_required"], name="reward_points_idx"),
        ]

    def __str__(self):
        return f"{self.name} - {self.points_required} points"

    def is_available(self):
        """Check if the reward is currently available for redemption."""
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if self.valid_from and now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        if self.quantity_available is not None:
            if self.quantity_redeemed >= self.quantity_available:
                return False
        
        return True


class RewardRedemption(models.Model):
    """Record of a reward redemption by a user."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    user = models.ForeignKey(
        User,
        related_name="reward_redemptions",
        on_delete=models.CASCADE,
        help_text="User who redeemed the reward",
    )
    reward = models.ForeignKey(
        Reward,
        related_name="redemptions",
        on_delete=models.CASCADE,
        help_text="Reward that was redeemed",
    )
    points_spent = models.IntegerField(
        help_text="Points spent to redeem this reward"
    )
    redemption_code = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique code for this redemption (e.g., discount code, voucher code)",
    )
    is_used = models.BooleanField(
        default=False, help_text="Whether this redemption has been used"
    )
    used_at = models.DateTimeField(
        null=True, blank=True, help_text="When the redemption was used"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this redemption expires (if applicable)",
    )

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            BTreeIndex(fields=["user"], name="reward_redemption_user_idx"),
            BTreeIndex(fields=["reward"], name="reward_redemption_reward_idx"),
            BTreeIndex(fields=["redemption_code"], name="reward_redemption_code_idx"),
            BTreeIndex(fields=["is_used"], name="reward_redemption_used_idx"),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.reward.name} - {self.redemption_code}"




