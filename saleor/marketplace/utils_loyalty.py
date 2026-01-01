"""Utility functions for loyalty system."""

from decimal import Decimal
from typing import Optional
from uuid import uuid4

from django.conf import settings
from django.utils import timezone

from ..account.models import User
from ..order.models import Order


def get_or_create_loyalty_balance(user: User):
    """Get or create a loyalty points balance for a user."""
    from .models_loyalty import LoyaltyPointsBalance

    balance, created = LoyaltyPointsBalance.objects.get_or_create(
        user=user,
        defaults={
            "balance": 0,
            "lifetime_earned": 0,
            "lifetime_spent": 0,
        },
    )
    return balance


def create_points_transaction(
    user: User,
    points: int,
    transaction_type: str,
    description: str = "",
    order: Optional[Order] = None,
    expires_at: Optional[timezone.datetime] = None,
):
    """Create a loyalty points transaction record."""
    from .models_loyalty import LoyaltyPointsTransaction, LoyaltyPointsBalance

    # Get current balance
    balance = get_or_create_loyalty_balance(user)
    new_balance = balance.balance + points

    # Create transaction record
    transaction = LoyaltyPointsTransaction.objects.create(
        user=user,
        points=points,
        balance_after=new_balance,
        transaction_type=transaction_type,
        description=description,
        order=order,
        expires_at=expires_at,
    )

    return transaction


def award_points_for_order(user: User, order: Order, points_per_dollar: Decimal = Decimal("1.0")):
    """Award loyalty points for a completed order."""
    from .models_loyalty import LoyaltyPointsBalance

    # Calculate points based on order total (use direct field for simplicity)
    order_total = order.total_gross_amount or Decimal("0")
    points = int(order_total * points_per_dollar)
    
    if points <= 0:
        return None

    # Add points to balance
    balance = get_or_create_loyalty_balance(user)
    balance.add_points(
        points,
        description=f"Points from order #{order.number}",
        order=order,
    )

    return points


def check_and_award_badges(user: User, order: Optional[Order] = None):
    """Check if user qualifies for any badges and award them."""
    from .models_loyalty import Badge, UserBadge, LoyaltyPointsBalance

    # Get all active badges
    badges = Badge.objects.filter(is_active=True)

    for badge in badges:
        # Skip if user already has this badge
        if UserBadge.objects.filter(user=user, badge=badge).exists():
            continue

        # Check if user meets criteria
        qualifies = False

        if badge.criteria_type == "order_count":
            from ..order.models import Order, OrderStatus
            order_count = Order.objects.filter(
                user=user, status__in=[OrderStatus.FULFILLED, OrderStatus.PARTIALLY_FULFILLED]
            ).count()
            if badge.criteria_value and order_count >= badge.criteria_value:
                qualifies = True

        elif badge.criteria_type == "total_spent":
            from ..order.models import Order, OrderStatus
            from django.db.models import Sum
            total_spent = (
                Order.objects.filter(
                    user=user, status__in=[OrderStatus.FULFILLED, OrderStatus.PARTIALLY_FULFILLED]
                ).aggregate(total=Sum("total_gross_amount"))["total"]
                or Decimal("0")
            )
            if badge.criteria_value and total_spent >= Decimal(str(badge.criteria_value)):
                qualifies = True

        elif badge.criteria_type == "loyalty_points":
            balance = get_or_create_loyalty_balance(user)
            if badge.criteria_value and balance.lifetime_earned >= badge.criteria_value:
                qualifies = True

        elif badge.criteria_type == "manual":
            # Manual badges must be assigned by staff
            continue

        if qualifies:
            # Award the badge
            UserBadge.objects.create(
                user=user,
                badge=badge,
                order=order,
            )

            # Award points if configured
            if badge.points_reward > 0:
                balance = get_or_create_loyalty_balance(user)
                balance.add_points(
                    badge.points_reward,
                    description=f"Points for earning badge: {badge.name}",
                )


def redeem_reward(user: User, reward, generate_code_func=None):
    """Redeem a reward for a user using their loyalty points."""
    from .models_loyalty import (
        LoyaltyPointsBalance,
        RewardRedemption,
    )

    # Check if reward is available
    if not reward.is_available():
        raise ValueError("Reward is not available for redemption")

    # Get user's balance
    balance = get_or_create_loyalty_balance(user)

    # Check if user has enough points
    if balance.balance < reward.points_required:
        raise ValueError("Insufficient points to redeem this reward")

    # Generate redemption code
    if generate_code_func:
        redemption_code = generate_code_func(reward)
    else:
        redemption_code = f"REDEEM-{uuid4().hex[:12].upper()}"

    # Spend points
    balance.spend_points(
        reward.points_required,
        description=f"Redeemed reward: {reward.name}",
    )

    # Create redemption record
    redemption = RewardRedemption.objects.create(
        user=user,
        reward=reward,
        points_spent=reward.points_required,
        redemption_code=redemption_code,
    )

    # Update reward redemption count
    reward.quantity_redeemed += 1
    reward.save(update_fields=["quantity_redeemed", "updated_at"])

    return redemption

