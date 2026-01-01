"""GraphQL resolvers for loyalty system."""

from typing import Optional

from ..core.context import get_database_connection_name
from saleor.marketplace import models_loyalty, utils_loyalty
from ..core import ResolveInfo
from ..core.validators import validate_one_of_args_is_in_query
from .types_loyalty import (
    Badge,
    LoyaltyPointsBalance,
    LoyaltyPointsTransaction,
    Reward,
    UserBadge,
)


def resolve_loyalty_balance(info: ResolveInfo, user_id: Optional[str] = None):
    """Resolve loyalty points balance for a user."""
    user = info.context.user

    # If user_id is provided, check permissions
    if user_id:
        from ..core.utils import from_global_id_or_error
        from ..account.types import User

        _, db_user_id = from_global_id_or_error(user_id, User)

        # Users can only view their own balance unless they're staff
        if not user.is_authenticated or (str(user.id) != str(db_user_id) and not user.is_staff):
            return None

        target_user_id = db_user_id
    else:
        # No user_id provided - return current user's balance
        if not user.is_authenticated:
            return None
        target_user_id = user.id

    connection_name = get_database_connection_name(info.context)
    balance = models_loyalty.LoyaltyPointsBalance.objects.using(
        connection_name
    ).filter(user_id=target_user_id).first()

    if not balance:
        # Create balance if it doesn't exist
        from ...account.models import User
        target_user = User.objects.using(connection_name).get(id=target_user_id)
        balance = utils_loyalty.get_or_create_loyalty_balance(target_user)

    return balance


def resolve_loyalty_points_transactions(
    info: ResolveInfo, user_id: Optional[str] = None, **kwargs
):
    """Resolve loyalty points transactions for a user."""
    user = info.context.user

    # If user_id is provided, check permissions
    if user_id:
        from ..core.utils import from_global_id_or_error
        from ..account.types import User

        _, db_user_id = from_global_id_or_error(user_id, User)

        # Users can only view their own transactions unless they're staff
        if not user.is_authenticated or (str(user.id) != str(db_user_id) and not user.is_staff):
            return models_loyalty.LoyaltyPointsTransaction.objects.none()

        target_user_id = db_user_id
    else:
        # No user_id provided - return current user's transactions
        if not user.is_authenticated:
            return models_loyalty.LoyaltyPointsTransaction.objects.none()
        target_user_id = user.id

    connection_name = get_database_connection_name(info.context)
    return models_loyalty.LoyaltyPointsTransaction.objects.using(
        connection_name
    ).filter(user_id=target_user_id)


def resolve_user_badges(info: ResolveInfo, user_id: Optional[str] = None, **kwargs):
    """Resolve badges earned by a user."""
    user = info.context.user

    # If user_id is provided, check permissions
    if user_id:
        from ..core.utils import from_global_id_or_error
        from ..account.types import User

        _, db_user_id = from_global_id_or_error(user_id, User)

        # Users can only view their own badges unless they're staff
        if not user.is_authenticated or (str(user.id) != str(db_user_id) and not user.is_staff):
            return models_loyalty.UserBadge.objects.none()

        target_user_id = db_user_id
    else:
        # No user_id provided - return current user's badges
        if not user.is_authenticated:
            return models_loyalty.UserBadge.objects.none()
        target_user_id = user.id

    connection_name = get_database_connection_name(info.context)
    return models_loyalty.UserBadge.objects.using(connection_name).filter(
        user_id=target_user_id
    )


def resolve_rewards(info: ResolveInfo, is_active: Optional[bool] = True, **kwargs):
    """Resolve available rewards."""
    connection_name = get_database_connection_name(info.context)
    qs = models_loyalty.Reward.objects.using(connection_name).all()

    if is_active is not None:
        qs = qs.filter(is_active=is_active)

    return qs


def resolve_badges(info: ResolveInfo, is_active: Optional[bool] = True, **kwargs):
    """Resolve available badges."""
    connection_name = get_database_connection_name(info.context)
    qs = models_loyalty.Badge.objects.using(connection_name).all()

    if is_active is not None:
        qs = qs.filter(is_active=is_active)

    return qs


def resolve_badge(info: ResolveInfo, id: Optional[str] = None, slug: Optional[str] = None):
    """Resolve a single badge by ID or slug."""
    validate_one_of_args_is_in_query("id", id, "slug", slug)

    connection_name = get_database_connection_name(info.context)
    qs = models_loyalty.Badge.objects.using(connection_name)

    if id:
        from ...graphql.core.utils import from_global_id_or_error
        from .types_loyalty import Badge

        _, badge_pk = from_global_id_or_error(id, Badge)
        return qs.filter(pk=badge_pk).first()

    if slug:
        return qs.filter(slug=slug).first()

    return None


def resolve_reward(info: ResolveInfo, id: Optional[str] = None, slug: Optional[str] = None):
    """Resolve a single reward by ID or slug."""
    validate_one_of_args_is_in_query("id", id, "slug", slug)

    connection_name = get_database_connection_name(info.context)
    qs = models_loyalty.Reward.objects.using(connection_name)

    if id:
        from ..core.utils import from_global_id_or_error
        from .types_loyalty import Reward

        _, reward_pk = from_global_id_or_error(id, Reward)
        return qs.filter(pk=reward_pk).first()

    if slug:
        return qs.filter(slug=slug).first()

    return None


def resolve_reward_redemptions(
    info: ResolveInfo, user_id: Optional[str] = None, **kwargs
):
    """Resolve reward redemptions for a user."""
    user = info.context.user

    # If user_id is provided, check permissions
    if user_id:
        from ..core.utils import from_global_id_or_error
        from ..account.types import User

        _, db_user_id = from_global_id_or_error(user_id, User)

        # Users can only view their own redemptions unless they're staff
        if not user.is_authenticated or (str(user.id) != str(db_user_id) and not user.is_staff):
            return models_loyalty.RewardRedemption.objects.none()

        target_user_id = db_user_id
    else:
        # No user_id provided - return current user's redemptions
        if not user.is_authenticated:
            return models_loyalty.RewardRedemption.objects.none()
        target_user_id = user.id

    connection_name = get_database_connection_name(info.context)
    return models_loyalty.RewardRedemption.objects.using(connection_name).filter(
        user_id=target_user_id
    )

