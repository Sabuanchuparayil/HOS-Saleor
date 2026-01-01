"""GraphQL mutation for redeeming a loyalty reward."""

import graphene
from django.core.exceptions import ValidationError

from ...core.context import get_database_connection_name
from ...core import ResolveInfo
from ...core.mutations import BaseMutation
from ...core.types.common import MarketplaceError
from ...core.utils import from_global_id_or_error
from ....marketplace import error_codes, models_loyalty, utils_loyalty
from ..types_loyalty import RewardRedemption


class LoyaltyRedeemReward(BaseMutation):
    """Redeem a reward using loyalty points."""

    class Arguments:
        reward_id = graphene.ID(required=True, description="ID of the reward to redeem.")

    class Meta:
        description = "Redeem a reward using loyalty points."
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    redemption = graphene.Field(RewardRedemption, description="The redemption record")

    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        """Redeem reward."""
        user = info.context.user
        if not user or not user.is_authenticated:
            raise ValidationError(
                {
                    "user": ValidationError(
                        "You must be authenticated to redeem rewards.",
                        code=error_codes.MarketplaceErrorCode.INVALID.value,
                    )
                }
            )

        reward_id = data.get("reward_id")

        if not reward_id:
            raise ValidationError(
                {
                    "rewardId": ValidationError(
                        "Reward ID is required.",
                        code=error_codes.MarketplaceErrorCode.REQUIRED.value,
                    )
                }
            )

        # Resolve reward ID
        _, reward_pk = from_global_id_or_error(reward_id, "Reward")

        # Get reward
        connection_name = get_database_connection_name(info.context)
        try:
            reward = models_loyalty.Reward.objects.using(connection_name).get(
                pk=reward_pk
            )
        except models_loyalty.Reward.DoesNotExist:
            raise ValidationError(
                {
                    "rewardId": ValidationError(
                        "Reward not found.",
                        code=error_codes.MarketplaceErrorCode.NOT_FOUND.value,
                    )
                }
            )

        # Redeem reward
        try:
            redemption = utils_loyalty.redeem_reward(user, reward)
        except ValueError as e:
            raise ValidationError(
                {"rewardId": ValidationError(str(e), code=error_codes.MarketplaceErrorCode.INVALID.value)}
            )

        return cls(redemption=redemption)

