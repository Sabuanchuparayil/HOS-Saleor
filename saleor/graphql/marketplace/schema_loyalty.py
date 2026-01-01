"""GraphQL schema for loyalty system."""

import graphene

from ..core.connection import CountableConnection, create_connection_slice
from ..core.doc_category import DOC_CATEGORY_MARKETPLACE
from ..core.fields import BaseField, ConnectionField
from .mutations.loyalty_redeem_reward import LoyaltyRedeemReward
from .resolvers_loyalty import (
    resolve_badge,
    resolve_badges,
    resolve_loyalty_balance,
    resolve_loyalty_points_transactions,
    resolve_reward,
    resolve_reward_redemptions,
    resolve_rewards,
    resolve_user_badges,
)
from .types_loyalty import (
    Badge,
    LoyaltyPointsBalance,
    LoyaltyPointsTransaction,
    Reward,
    RewardRedemption,
    UserBadge,
)


class LoyaltyPointsBalanceQueries(graphene.ObjectType):
    """Queries for loyalty points balance."""

    loyalty_points_balance = BaseField(
        LoyaltyPointsBalance,
        user_id=graphene.Argument(
            graphene.ID,
            description="ID of the user (defaults to authenticated user)",
        ),
        description="Get loyalty points balance for a user.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )

    @staticmethod
    def resolve_loyalty_points_balance(_root, info, user_id=None):
        return resolve_loyalty_balance(info, user_id=user_id)


class LoyaltyPointsTransactionCountableConnection(CountableConnection):
    """Connection type for LoyaltyPointsTransaction list queries."""

    class Meta:
        node = LoyaltyPointsTransaction
        doc_category = DOC_CATEGORY_MARKETPLACE


class LoyaltyPointsTransactionQueries(graphene.ObjectType):
    """Queries for loyalty points transactions."""

    loyalty_points_transactions = ConnectionField(
        LoyaltyPointsTransactionCountableConnection,
        user_id=graphene.Argument(
            graphene.ID,
            description="ID of the user (defaults to authenticated user)",
        ),
        description="List of loyalty points transactions for a user.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )

    @staticmethod
    def resolve_loyalty_points_transactions(_root, info, user_id=None, **kwargs):
        qs = resolve_loyalty_points_transactions(info, user_id=user_id)
        return create_connection_slice(
            qs, info, kwargs, LoyaltyPointsTransactionCountableConnection
        )


class BadgeCountableConnection(CountableConnection):
    """Connection type for Badge list queries."""

    class Meta:
        node = Badge
        doc_category = DOC_CATEGORY_MARKETPLACE


class BadgeQueries(graphene.ObjectType):
    """Queries for badges."""

    badge = BaseField(
        Badge,
        id=graphene.Argument(graphene.ID, description="ID of the badge."),
        slug=graphene.Argument(graphene.String, description="Slug of the badge."),
        description="Look up a badge by ID or slug.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )
    badges = ConnectionField(
        BadgeCountableConnection,
        is_active=graphene.Argument(
            graphene.Boolean, description="Filter by active status."
        ),
        description="List of badges.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )

    @staticmethod
    def resolve_badge(_root, info, id=None, slug=None):
        return resolve_badge(info, id, slug)

    @staticmethod
    def resolve_badges(_root, info, is_active=None, **kwargs):
        qs = resolve_badges(info, is_active=is_active)
        return create_connection_slice(qs, info, kwargs, BadgeCountableConnection)


class UserBadgeCountableConnection(CountableConnection):
    """Connection type for UserBadge list queries."""

    class Meta:
        node = UserBadge
        doc_category = DOC_CATEGORY_MARKETPLACE


class UserBadgeQueries(graphene.ObjectType):
    """Queries for user badges."""

    user_badges = ConnectionField(
        UserBadgeCountableConnection,
        user_id=graphene.Argument(
            graphene.ID,
            description="ID of the user (defaults to authenticated user)",
        ),
        description="List of badges earned by a user.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )

    @staticmethod
    def resolve_user_badges(_root, info, user_id=None, **kwargs):
        qs = resolve_user_badges(info, user_id=user_id)
        return create_connection_slice(qs, info, kwargs, UserBadgeCountableConnection)


class RewardCountableConnection(CountableConnection):
    """Connection type for Reward list queries."""

    class Meta:
        node = Reward
        doc_category = DOC_CATEGORY_MARKETPLACE


class RewardQueries(graphene.ObjectType):
    """Queries for rewards."""

    reward = BaseField(
        Reward,
        id=graphene.Argument(graphene.ID, description="ID of the reward."),
        slug=graphene.Argument(graphene.String, description="Slug of the reward."),
        description="Look up a reward by ID or slug.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )
    rewards = ConnectionField(
        RewardCountableConnection,
        is_active=graphene.Argument(
            graphene.Boolean, description="Filter by active status."
        ),
        description="List of available rewards.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )

    @staticmethod
    def resolve_reward(_root, info, id=None, slug=None):
        return resolve_reward(info, id, slug)

    @staticmethod
    def resolve_rewards(_root, info, is_active=None, **kwargs):
        qs = resolve_rewards(info, is_active=is_active)
        return create_connection_slice(qs, info, kwargs, RewardCountableConnection)


class RewardRedemptionCountableConnection(CountableConnection):
    """Connection type for RewardRedemption list queries."""

    class Meta:
        node = RewardRedemption
        doc_category = DOC_CATEGORY_MARKETPLACE


class RewardRedemptionQueries(graphene.ObjectType):
    """Queries for reward redemptions."""

    reward_redemptions = ConnectionField(
        RewardRedemptionCountableConnection,
        user_id=graphene.Argument(
            graphene.ID,
            description="ID of the user (defaults to authenticated user)",
        ),
        description="List of reward redemptions for a user.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )

    @staticmethod
    def resolve_reward_redemptions(_root, info, user_id=None, **kwargs):
        qs = resolve_reward_redemptions(info, user_id=user_id)
        return create_connection_slice(
            qs, info, kwargs, RewardRedemptionCountableConnection
        )


class LoyaltyMutations(graphene.ObjectType):
    """Mutations for loyalty system."""

    loyalty_redeem_reward = LoyaltyRedeemReward.Field()

