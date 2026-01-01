"""GraphQL types for loyalty system."""

import graphene
from graphene import relay

from ...marketplace import models_loyalty
from ..core.doc_category import DOC_CATEGORY_MARKETPLACE
from ..core.scalars import DateTime
from ..core.types import Image, ModelObjectType, Money
from .enums_loyalty import (
    BadgeCriteriaTypeEnum,
    LoyaltyPointsTransactionTypeEnum,
    LoyaltyRewardTypeEnum,
)


class LoyaltyPointsBalance(ModelObjectType[models_loyalty.LoyaltyPointsBalance]):
    """Current loyalty points balance for a user."""

    class Meta:
        description = "Current loyalty points balance for a user."
        model = models_loyalty.LoyaltyPointsBalance
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    user = graphene.Field("saleor.graphql.account.types.User", required=True)
    balance = graphene.Int(required=True, description="Current points balance")
    lifetime_earned = graphene.Int(
        required=True, description="Total points ever earned"
    )
    lifetime_spent = graphene.Int(required=True, description="Total points ever spent")
    created_at = DateTime(required=True)
    updated_at = DateTime(required=True)


class LoyaltyPointsTransaction(ModelObjectType[models_loyalty.LoyaltyPointsTransaction]):
    """Record of a loyalty points transaction."""

    class Meta:
        description = "Record of a loyalty points transaction (earned or spent)."
        model = models_loyalty.LoyaltyPointsTransaction
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    user = graphene.Field("saleor.graphql.account.types.User", required=True)
    points = graphene.Int(
        required=True,
        description="Number of points (positive for earned, negative for spent)",
    )
    balance_after = graphene.Int(
        required=True, description="User's balance after this transaction"
    )
    transaction_type = LoyaltyPointsTransactionTypeEnum(
        required=True, description="Type of transaction"
    )
    description = graphene.String(description="Description of the transaction")
    order = graphene.Field("saleor.graphql.order.types.Order")
    created_at = DateTime(required=True)
    expires_at = DateTime(description="When these points expire")


class Badge(ModelObjectType[models_loyalty.Badge]):
    """Definition of a badge that users can earn."""

    class Meta:
        description = "Definition of a badge that users can earn."
        model = models_loyalty.Badge
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True, description="Name of the badge")
    slug = graphene.String(required=True, description="Unique slug for the badge")
    description = graphene.String(description="Description of what the badge represents")
    icon = graphene.Field(Image, description="Badge icon/image")
    is_active = graphene.Boolean(
        required=True, description="Whether this badge is currently active"
    )
    criteria_type = BadgeCriteriaTypeEnum(
        required=True, description="Type of criteria for earning this badge"
    )
    criteria_value = graphene.Int(
        description="Value required to earn this badge (e.g., 10 orders, 1000 points)"
    )
    points_reward = graphene.Int(
        required=True,
        description="Points awarded when this badge is earned",
    )
    created_at = DateTime(required=True)
    updated_at = DateTime(required=True)


class UserBadge(ModelObjectType[models_loyalty.UserBadge]):
    """Record of a badge earned by a user."""

    class Meta:
        description = "Record of a badge earned by a user."
        model = models_loyalty.UserBadge
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    user = graphene.Field("saleor.graphql.account.types.User", required=True)
    badge = graphene.Field(Badge, required=True)
    earned_at = DateTime(
        required=True, description="When the badge was earned"
    )
    order = graphene.Field("saleor.graphql.order.types.Order")


class Reward(ModelObjectType[models_loyalty.Reward]):
    """Definition of a reward that can be redeemed with loyalty points."""

    class Meta:
        description = "Definition of a reward that can be redeemed with loyalty points."
        model = models_loyalty.Reward
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True, description="Name of the reward")
    slug = graphene.String(required=True, description="Unique slug for the reward")
    description = graphene.String(description="Description of the reward")
    points_required = graphene.Int(
        required=True, description="Points required to redeem this reward"
    )
    reward_type = LoyaltyRewardTypeEnum(required=True, description="Type of reward")
    reward_value = graphene.Field(
        Money, description="Value of the reward (e.g., discount amount, voucher amount)"
    )
    product = graphene.Field(
        "saleor.graphql.product.types.products.Product",
        description="Product for free product rewards",
    )
    is_active = graphene.Boolean(
        required=True, description="Whether this reward is currently available"
    )
    is_available = graphene.Boolean(
        required=True, description="Whether this reward is currently available for redemption"
    )
    quantity_available = graphene.Int(
        description="Number of times this reward can be redeemed (null = unlimited)"
    )
    quantity_redeemed = graphene.Int(
        required=True, description="Number of times this reward has been redeemed"
    )
    valid_from = DateTime(description="When this reward becomes available")
    valid_until = DateTime(description="When this reward expires")
    created_at = DateTime(required=True)
    updated_at = DateTime(required=True)

    @staticmethod
    def resolve_reward_value(root: models_loyalty.Reward, info):
        """Resolve reward value as Money."""
        if root.reward_value:
            # Assume default currency - in production, this should come from channel/settings
            from ...core.prices import Money
            return Money(root.reward_value, "USD")
        return None

    @staticmethod
    def resolve_is_available(root: models_loyalty.Reward, info):
        """Check if reward is currently available."""
        return root.is_available()


class RewardRedemption(ModelObjectType[models_loyalty.RewardRedemption]):
    """Record of a reward redemption by a user."""

    class Meta:
        description = "Record of a reward redemption by a user."
        model = models_loyalty.RewardRedemption
        interfaces = [relay.Node]
        doc_category = DOC_CATEGORY_MARKETPLACE

    id = graphene.GlobalID(required=True)
    user = graphene.Field("saleor.graphql.account.types.User", required=True)
    reward = graphene.Field(Reward, required=True)
    points_spent = graphene.Int(
        required=True, description="Points spent to redeem this reward"
    )
    redemption_code = graphene.String(
        required=True,
        description="Unique code for this redemption (e.g., discount code, voucher code)",
    )
    is_used = graphene.Boolean(
        required=True, description="Whether this redemption has been used"
    )
    used_at = DateTime(description="When the redemption was used")
    expires_at = DateTime(description="When this redemption expires")
    created_at = DateTime(required=True)

