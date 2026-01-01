"""GraphQL input types for loyalty system."""

import graphene

from ..core.doc_category import DOC_CATEGORY_MARKETPLACE
from ..core.types import BaseInputObjectType


class RewardRedeemInput(BaseInputObjectType):
    """Input type for redeeming a reward."""

    reward_id = graphene.ID(
        required=True, description="ID of the reward to redeem"
    )


class LoyaltyPointsAdjustInput(BaseInputObjectType):
    """Input type for adjusting loyalty points (staff only)."""

    user_id = graphene.ID(required=True, description="ID of the user")
    points = graphene.Int(
        required=True,
        description="Number of points to add (positive) or subtract (negative)",
    )
    description = graphene.String(
        description="Description of the adjustment"
    )




