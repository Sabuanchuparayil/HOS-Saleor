"""GraphQL enums for loyalty system."""

import graphene

from ...marketplace import models_loyalty


class LoyaltyPointsTransactionTypeEnum(graphene.Enum):
    """Transaction type for loyalty points."""

    EARNED = "earned"
    SPENT = "spent"
    EXPIRED = "expired"
    ADJUSTED = "adjusted"

    @property
    def description(self):
        if self == LoyaltyPointsTransactionTypeEnum.EARNED:
            return "Points were earned"
        elif self == LoyaltyPointsTransactionTypeEnum.SPENT:
            return "Points were spent"
        elif self == LoyaltyPointsTransactionTypeEnum.EXPIRED:
            return "Points expired"
        elif self == LoyaltyPointsTransactionTypeEnum.ADJUSTED:
            return "Points were adjusted by staff"
        return None


class BadgeCriteriaTypeEnum(graphene.Enum):
    """Criteria type for badge earning."""

    ORDER_COUNT = "order_count"
    TOTAL_SPENT = "total_spent"
    LOYALTY_POINTS = "loyalty_points"
    MANUAL = "manual"

    @property
    def description(self):
        if self == BadgeCriteriaTypeEnum.ORDER_COUNT:
            return "Based on number of orders"
        elif self == BadgeCriteriaTypeEnum.TOTAL_SPENT:
            return "Based on total amount spent"
        elif self == BadgeCriteriaTypeEnum.LOYALTY_POINTS:
            return "Based on lifetime loyalty points earned"
        elif self == BadgeCriteriaTypeEnum.MANUAL:
            return "Manually assigned by staff"
        return None


class LoyaltyRewardTypeEnum(graphene.Enum):
    """Type of loyalty reward."""

    DISCOUNT = "discount"
    PRODUCT = "product"
    VOUCHER = "voucher"
    SHIPPING = "shipping"

    @property
    def description(self):
        if self == LoyaltyRewardTypeEnum.DISCOUNT:
            return "Discount code reward"
        elif self == LoyaltyRewardTypeEnum.PRODUCT:
            return "Free product reward"
        elif self == LoyaltyRewardTypeEnum.VOUCHER:
            return "Gift voucher reward"
        elif self == LoyaltyRewardTypeEnum.SHIPPING:
            return "Free shipping reward"
        return None

