"""GraphQL mutations for marketplace."""

from .loyalty_redeem_reward import LoyaltyRedeemReward
from .newsletter_subscribe import NewsletterSubscribe, NewsletterUnsubscribe
from .pricing_rule_create import PricingRuleCreate
from .product_submission_approve import ProductSubmissionApprove
from .product_view import ProductView
from .return_request_create import ReturnRequestCreate
from .return_request_process import ReturnRequestProcess
from .seller_approve import SellerApprove
from .seller_create import SellerCreate
from .seller_delete import SellerDelete
from .seller_domain_add import SellerDomainAdd
from .seller_domain_remove import SellerDomainRemove
from .seller_domain_verify import SellerDomainVerify
from .inventory_sync_request import InventorySyncRequest
from .seller_credit_terms_update import SellerCreditTermsUpdate
from .seller_logistics_config_update import SellerLogisticsConfigUpdate
from .seller_product_create import SellerProductCreate
from .seller_shipping_method_create import SellerShippingMethodCreate
from .seller_shipping_method_delete import SellerShippingMethodDelete
from .seller_shipping_method_update import SellerShippingMethodUpdate
from .seller_storefront_settings_update import SellerStorefrontSettingsUpdate
from .seller_update import SellerUpdate
from .theme_create import ThemeCreate
from .theme_delete import ThemeDelete
from .theme_update import ThemeUpdate
from .user_preferences_update import UserPreferencesUpdate

__all__ = [
    "SellerApprove",
    "SellerCreate",
    "SellerUpdate",
    "SellerDelete",
    "SellerDomainAdd",
    "SellerDomainRemove",
    "SellerDomainVerify",
    "SellerStorefrontSettingsUpdate",
    "SellerLogisticsConfigUpdate",
    "SellerProductCreate",
    "SellerShippingMethodCreate",
    "SellerShippingMethodUpdate",
    "SellerShippingMethodDelete",
    "SellerCreditTermsUpdate",
    "InventorySyncRequest",
    "ThemeCreate",
    "ThemeUpdate",
    "ThemeDelete",
    "NewsletterSubscribe",
    "NewsletterUnsubscribe",
    "UserPreferencesUpdate",
    "ProductView",
    "ProductSubmissionApprove",
    "ReturnRequestCreate",
    "ReturnRequestProcess",
    "PricingRuleCreate",
    "LoyaltyRedeemReward",
]
