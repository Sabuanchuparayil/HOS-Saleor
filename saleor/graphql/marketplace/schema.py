"""GraphQL schema for marketplace."""

import graphene

from ..core.connection import CountableConnection, create_connection_slice
from ..core.doc_category import DOC_CATEGORY_MARKETPLACE
from ..core.fields import BaseField, ConnectionField
from .schema_loyalty import (
    BadgeQueries,
    LoyaltyMutations,
    LoyaltyPointsBalanceQueries,
    LoyaltyPointsTransactionQueries,
    RewardQueries,
    RewardRedemptionQueries,
    UserBadgeQueries,
)
from .mutations import (
      NewsletterSubscribe,
      NewsletterUnsubscribe,
      PricingRuleCreate,
      ProductSubmissionApprove,
      ProductView,
      ReturnRequestCreate,
      ReturnRequestProcess,
      SellerApprove,
      SellerCreate,
      SellerCreditTermsUpdate,
      SellerDelete,
      SellerDomainAdd,
      SellerDomainRemove,
      SellerDomainVerify,
      InventorySyncRequest,
      SellerLogisticsConfigUpdate,
      SellerProductCreate,
      SellerShippingMethodCreate,
      SellerShippingMethodDelete,
      SellerShippingMethodUpdate,
      SellerStorefrontSettingsUpdate,
      SellerUpdate,
      ThemeCreate,
      ThemeDelete,
      ThemeUpdate,
      UserPreferencesUpdate,
  )
from .resolvers import (
      resolve_default_theme,
      resolve_featured_collections,
      resolve_featured_products,
      resolve_fulfillment_center,
      resolve_fulfillment_centers,
      resolve_newsletter_subscription,
      resolve_newsletter_subscriptions,
      resolve_product_submission,
      resolve_product_submissions,
      resolve_recently_viewed_products,
      resolve_return_policy,
      resolve_return_policies,
      resolve_return_request,
      resolve_return_requests,
      resolve_seller,
      resolve_sellers,
      resolve_theme,
      resolve_themes,
      resolve_user_preferences,
  )
from .resolvers_shipping import (
      resolve_seller_shipping_method,
      resolve_seller_shipping_methods,
  )
from .resolvers_inventory import (
      resolve_inventory_sync,
      resolve_inventory_syncs,
  )
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
from .types import (
    FulfillmentCenter,
    NewsletterSubscription,
    ProductSubmission,
    ReturnPolicy,
    ReturnRequest,
    Seller,
    Theme,
    UserPreferences,
)
from .types_inventory import InventorySync
from .types_loyalty import (
      Badge,
      LoyaltyPointsBalance,
      LoyaltyPointsTransaction,
      Reward,
      RewardRedemption,
      UserBadge,
  )
from ..product.types import Collection, CollectionCountableConnection, Product, ProductCountableConnection


class SellerCountableConnection(CountableConnection):
    """Connection type for Seller list queries."""

    class Meta:
        node = Seller
        doc_category = DOC_CATEGORY_MARKETPLACE


class ThemeCountableConnection(CountableConnection):
    """Connection type for Theme list queries."""

    class Meta:
        node = Theme
        doc_category = DOC_CATEGORY_MARKETPLACE


class SellerQueries(graphene.ObjectType):
    """Queries for marketplace sellers."""

    seller = BaseField(
        Seller,
        id=graphene.Argument(graphene.ID, description="ID of the seller."),
        slug=graphene.Argument(graphene.String, description="Slug of the seller."),
        description="Look up a seller by ID or slug.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )
    sellers = ConnectionField(
        SellerCountableConnection,
        seller_type=graphene.Argument(
            "saleor.graphql.marketplace.enums.SellerTypeEnum",
            description="Filter sellers by seller type (B2B, B2C, Hybrid)."
        ),
        status=graphene.Argument(
            "saleor.graphql.marketplace.enums.SellerStatusEnum",
            description="Filter sellers by status."
        ),
        description="List of sellers.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )
    seller_orders = ConnectionField(
        "saleor.graphql.order.types.OrderCountableConnection",
        seller_id=graphene.Argument(
            graphene.ID, description="ID of the seller to get orders for."
        ),
        description="List of orders for a specific seller.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )
    seller_settlements = ConnectionField(
        "saleor.graphql.marketplace.types.SellerSettlementCountableConnection",
        seller_id=graphene.Argument(
            graphene.ID, description="ID of the seller to get settlements for."
        ),
        status=graphene.Argument(
            "saleor.graphql.marketplace.enums.SettlementStatusEnum",
            description="Filter settlements by status.",
        ),
        description="List of settlements/payouts for a specific seller.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )

    @staticmethod
    def resolve_seller(_root, info, id=None, slug=None):
        return resolve_seller(info, id, slug)

    @staticmethod
    def resolve_sellers(_root, info, seller_type=None, status=None, **kwargs):
        qs = resolve_sellers(info)
        
        # Apply seller type filter
        if seller_type:
            from saleor.marketplace.models import SellerType
            seller_type_value = seller_type.value if hasattr(seller_type, 'value') else seller_type
            qs = qs.filter(seller_type=seller_type_value)
        
        # Apply status filter
        if status:
            from saleor.marketplace.models import SellerStatus
            status_value = status.value if hasattr(status, 'value') else status
            qs = qs.filter(status=status_value)
        
        return create_connection_slice(qs, info, kwargs, SellerCountableConnection)

    @staticmethod
    def resolve_seller_orders(_root, info, seller_id, **kwargs):
        from .resolvers import resolve_seller_orders
        from ..order.types import OrderCountableConnection
        
        qs = resolve_seller_orders(info, seller_id)
        return create_connection_slice(qs, info, kwargs, OrderCountableConnection)

    @staticmethod
    def resolve_seller_settlements(_root, info, seller_id, status=None, **kwargs):
        from .resolvers import resolve_seller_settlements
        from .types import SellerSettlementCountableConnection
        
        qs = resolve_seller_settlements(info, seller_id, status)
        return create_connection_slice(qs, info, kwargs, SellerSettlementCountableConnection)


class ThemeQueries(graphene.ObjectType):
    """Queries for themes."""

    theme = BaseField(
        Theme,
        id=graphene.Argument(graphene.ID, description="ID of the theme."),
        slug=graphene.Argument(graphene.String, description="Slug of the theme."),
        description="Look up a theme by ID or slug.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )
    themes = ConnectionField(
        ThemeCountableConnection,
        is_active=graphene.Argument(
            graphene.Boolean, description="Filter by active status."
        ),
        description="List of themes.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )
    default_theme = BaseField(
        Theme,
        description="Get the default theme.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )

    @staticmethod
    def resolve_theme(_root, info, id=None, slug=None):
        return resolve_theme(info, id, slug)

    @staticmethod
    def resolve_themes(_root, info, is_active=None, **kwargs):
        qs = resolve_themes(info, is_active=is_active)
        return create_connection_slice(qs, info, kwargs, ThemeCountableConnection)

    @staticmethod
    def resolve_default_theme(_root, info):
        return resolve_default_theme(info)


class SellerMutations(graphene.ObjectType):
    """Mutations for marketplace sellers."""

    seller_create = SellerCreate.Field()
    seller_update = SellerUpdate.Field()
    seller_delete = SellerDelete.Field()
    seller_approve = SellerApprove.Field()
    seller_domain_add = SellerDomainAdd.Field()
    seller_domain_remove = SellerDomainRemove.Field()
    seller_domain_verify = SellerDomainVerify.Field()
    seller_storefront_settings_update = SellerStorefrontSettingsUpdate.Field()
    seller_logistics_config_update = SellerLogisticsConfigUpdate.Field()
    seller_product_create = SellerProductCreate.Field()
    seller_shipping_method_create = SellerShippingMethodCreate.Field()
    seller_shipping_method_update = SellerShippingMethodUpdate.Field()
    seller_shipping_method_delete = SellerShippingMethodDelete.Field()
    seller_credit_terms_update = SellerCreditTermsUpdate.Field()
    inventory_sync_request = InventorySyncRequest.Field()
    product_submission_approve = ProductSubmissionApprove.Field()
    return_request_create = ReturnRequestCreate.Field()
    return_request_process = ReturnRequestProcess.Field()
    pricing_rule_create = PricingRuleCreate.Field()


class ThemeMutations(graphene.ObjectType):
    """Mutations for themes."""

    theme_create = ThemeCreate.Field()
    theme_update = ThemeUpdate.Field()
    theme_delete = ThemeDelete.Field()


class NewsletterSubscriptionCountableConnection(CountableConnection):
    """Connection type for NewsletterSubscription list queries."""

    class Meta:
        node = NewsletterSubscription
        doc_category = DOC_CATEGORY_MARKETPLACE


class NewsletterQueries(graphene.ObjectType):
    """Queries for newsletter subscriptions."""

    newsletter_subscription = BaseField(
        NewsletterSubscription,
        id=graphene.Argument(graphene.ID, description="ID of the subscription."),
        email=graphene.Argument(graphene.String, description="Email of the subscription."),
        description="Look up a newsletter subscription by ID or email.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )
    newsletter_subscriptions = ConnectionField(
        NewsletterSubscriptionCountableConnection,
        is_active=graphene.Argument(
            graphene.Boolean, description="Filter by active status."
        ),
        description="List of newsletter subscriptions.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )

    @staticmethod
    def resolve_newsletter_subscription(_root, info, id=None, email=None):
        return resolve_newsletter_subscription(info, id, email)

    @staticmethod
    def resolve_newsletter_subscriptions(_root, info, is_active=None, **kwargs):
        qs = resolve_newsletter_subscriptions(info, is_active=is_active)
        return create_connection_slice(
            qs, info, kwargs, NewsletterSubscriptionCountableConnection
        )


class NewsletterSubscriptionCountableConnection(CountableConnection):
    """Connection type for NewsletterSubscription list queries."""

    class Meta:
        node = NewsletterSubscription
        doc_category = DOC_CATEGORY_MARKETPLACE


class NewsletterMutations(graphene.ObjectType):
    """Mutations for newsletter subscriptions."""

    newsletter_subscribe = NewsletterSubscribe.Field()
    newsletter_unsubscribe = NewsletterUnsubscribe.Field()


class UserPreferencesQueries(graphene.ObjectType):
    """Queries for user preferences."""

    user_preferences = BaseField(
        UserPreferences,
        description="Get user preferences for the authenticated user.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )

    @staticmethod
    def resolve_user_preferences(_root, info):
        return resolve_user_preferences(info)


class UserPreferencesMutations(graphene.ObjectType):
    """Mutations for user preferences."""

    user_preferences_update = UserPreferencesUpdate.Field()


class HomepageQueries(graphene.ObjectType):
    """Queries for homepage content."""

    featured_collections = ConnectionField(
        CollectionCountableConnection,
        channel=graphene.Argument(
            graphene.String,
            description="Slug of a channel for which the data should be returned."
        ),
        description="List of featured collections for homepage.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )
    featured_products = ConnectionField(
        ProductCountableConnection,
        channel=graphene.Argument(
            graphene.String,
            description="Slug of a channel for which the data should be returned."
        ),
        description="List of featured products for homepage.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )
    recently_viewed_products = ConnectionField(
        ProductCountableConnection,
        channel=graphene.Argument(
            graphene.String,
            description="Slug of a channel for which the data should be returned."
        ),
        description="List of recently viewed products for the authenticated user.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )

    @staticmethod
    def resolve_featured_collections(_root, info, channel=None, **kwargs):
        """Resolve featured collections for homepage."""
        from ...core.context import ChannelContext
        
        collections = resolve_featured_collections(
            info, channel=channel, first=kwargs.get("first")
        )
        
        # Wrap collections in ChannelContext for proper GraphQL resolution
        channel_contexts = [
            ChannelContext(node=collection, channel_slug=channel)
            for collection in collections
        ]
        
        return create_connection_slice(
            channel_contexts, info, kwargs, CollectionCountableConnection
        )

    @staticmethod
    def resolve_featured_products(_root, info, channel=None, **kwargs):
        """Resolve featured products for homepage."""
        from ...core.context import ChannelContext
        
        products = resolve_featured_products(
            info, channel=channel, first=kwargs.get("first")
        )
        
        # Wrap products in ChannelContext for proper GraphQL resolution
        channel_contexts = [
            ChannelContext(node=product, channel_slug=channel)
            for product in products
        ]
        
        return create_connection_slice(
            channel_contexts, info, kwargs, ProductCountableConnection
        )

    @staticmethod
    def resolve_recently_viewed_products(_root, info, channel=None, **kwargs):
        """Resolve recently viewed products for the authenticated user."""
        from ...core.context import ChannelContext
        
        products = resolve_recently_viewed_products(
            info, channel=channel, first=kwargs.get("first")
        )
        
        # Wrap products in ChannelContext for proper GraphQL resolution
        channel_contexts = [
            ChannelContext(node=product, channel_slug=channel)
            for product in products
        ]
        
        return create_connection_slice(
            channel_contexts, info, kwargs, ProductCountableConnection
        )


class FulfillmentCenterQueries(graphene.ObjectType):
    """Queries for fulfillment centers."""

    fulfillment_center = BaseField(
        FulfillmentCenter,
        id=graphene.Argument(graphene.ID, description="ID of the fulfillment center."),
        description="Look up a fulfillment center by ID.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )
    fulfillment_centers = ConnectionField(
        "saleor.graphql.marketplace.types.FulfillmentCenterCountableConnection",
        is_active=graphene.Argument(
            graphene.Boolean, description="Filter by active status."
        ),
        description="List of fulfillment centers.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )

    @staticmethod
    def resolve_fulfillment_center(_root, info, id):
        return resolve_fulfillment_center(info, id)

    @staticmethod
    def resolve_fulfillment_centers(_root, info, is_active=None, **kwargs):
        from .types import FulfillmentCenterCountableConnection
        
        qs = resolve_fulfillment_centers(info, is_active=is_active)
        return create_connection_slice(qs, info, kwargs, FulfillmentCenterCountableConnection)


class ProductSubmissionQueries(graphene.ObjectType):
    """Queries for product submissions."""

    product_submission = BaseField(
        ProductSubmission,
        id=graphene.Argument(graphene.ID, description="ID of the product submission."),
        description="Look up a product submission by ID.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )
    product_submissions = ConnectionField(
        "saleor.graphql.marketplace.types.ProductSubmissionCountableConnection",
        seller_id=graphene.Argument(
            graphene.ID, description="Filter by seller ID."
        ),
        status=graphene.Argument(
            "saleor.graphql.marketplace.enums.ProductApprovalStatusEnum",
            description="Filter by approval status.",
        ),
        description="List of product submissions.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )

    @staticmethod
    def resolve_product_submission(_root, info, id):
        return resolve_product_submission(info, id)

    @staticmethod
    def resolve_product_submissions(_root, info, seller_id=None, status=None, **kwargs):
        from .types import ProductSubmissionCountableConnection
        
        qs = resolve_product_submissions(info, seller_id=seller_id, status=status)
        return create_connection_slice(qs, info, kwargs, ProductSubmissionCountableConnection)


class SellerShippingMethodQueries(graphene.ObjectType):
    """Queries for seller shipping methods."""

    seller_shipping_method = BaseField(
        "saleor.graphql.marketplace.types.SellerShippingMethod",
        id=graphene.Argument(graphene.ID, description="ID of the shipping method."),
        description="Look up a seller shipping method by ID.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )
    seller_shipping_methods = ConnectionField(
        "saleor.graphql.marketplace.types.SellerShippingMethodCountableConnection",
        seller_id=graphene.Argument(
            graphene.ID, description="Filter by seller ID."
        ),
        is_active=graphene.Argument(
            graphene.Boolean, description="Filter by active status."
        ),
        description="List of seller shipping methods.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )

    @staticmethod
    def resolve_seller_shipping_method(_root, info, id):
        return resolve_seller_shipping_method(info, id)

    @staticmethod
    def resolve_seller_shipping_methods(_root, info, seller_id=None, is_active=None, **kwargs):
        from .types import SellerShippingMethodCountableConnection
        
        qs = resolve_seller_shipping_methods(info, seller_id=seller_id, is_active=is_active)
        return create_connection_slice(qs, info, kwargs, SellerShippingMethodCountableConnection)


class InventorySyncQueries(graphene.ObjectType):
    """Queries for inventory synchronization."""

    inventory_sync = BaseField(
        "saleor.graphql.marketplace.types_inventory.InventorySync",
        id=graphene.Argument(graphene.ID, description="ID of the inventory sync."),
        description="Look up an inventory sync by ID.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )
    inventory_syncs = ConnectionField(
        "saleor.graphql.marketplace.types_inventory.InventorySyncCountableConnection",
        product_variant_id=graphene.Argument(
            graphene.ID, description="Filter by product variant ID."
        ),
        fulfillment_center_id=graphene.Argument(
            graphene.ID, description="Filter by fulfillment center ID."
        ),
        warehouse_id=graphene.Argument(
            graphene.ID, description="Filter by warehouse ID."
        ),
        description="List of inventory syncs.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )

    @staticmethod
    def resolve_inventory_sync(_root, info, id):
        return resolve_inventory_sync(info, id)

    @staticmethod
    def resolve_inventory_syncs(
        _root,
        info,
        product_variant_id=None,
        fulfillment_center_id=None,
        warehouse_id=None,
        **kwargs
    ):
        from .types_inventory import InventorySyncCountableConnection

        qs = resolve_inventory_syncs(
            info,
            product_variant_id=product_variant_id,
            fulfillment_center_id=fulfillment_center_id,
            warehouse_id=warehouse_id,
        )
        return create_connection_slice(qs, info, kwargs, InventorySyncCountableConnection)


class ReturnRequestQueries(graphene.ObjectType):
    """Queries for return requests."""

    return_request = BaseField(
        ReturnRequest,
        id=graphene.Argument(graphene.ID, description="ID of the return request."),
        description="Look up a return request by ID.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )
    return_requests = ConnectionField(
        "saleor.graphql.marketplace.types.ReturnRequestCountableConnection",
        order_id=graphene.Argument(
            graphene.ID, description="Filter by order ID."
        ),
        status=graphene.Argument(
            "saleor.graphql.marketplace.enums.ReturnRequestStatusEnum",
            description="Filter by status.",
        ),
        description="List of return requests.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )

    @staticmethod
    def resolve_return_request(_root, info, id):
        return resolve_return_request(info, id)

    @staticmethod
    def resolve_return_requests(_root, info, order_id=None, status=None, **kwargs):
        from .types import ReturnRequestCountableConnection
        
        qs = resolve_return_requests(info, order_id=order_id, status=status)
        return create_connection_slice(qs, info, kwargs, ReturnRequestCountableConnection)


class ReturnPolicyQueries(graphene.ObjectType):
    """Queries for return policies."""

    return_policy = BaseField(
        ReturnPolicy,
        id=graphene.Argument(graphene.ID, description="ID of the return policy."),
        description="Look up a return policy by ID.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )
    return_policies = ConnectionField(
        "saleor.graphql.marketplace.types.ReturnPolicyCountableConnection",
        seller_id=graphene.Argument(graphene.ID, description="Filter by seller ID."),
        product_id=graphene.Argument(graphene.ID, description="Filter by product ID."),
        is_active=graphene.Argument(graphene.Boolean, description="Filter by active flag."),
        description="List of return policies.",
        doc_category=DOC_CATEGORY_MARKETPLACE,
    )

    @staticmethod
    def resolve_return_policy(_root, info, id):
        return resolve_return_policy(info, id)

    @staticmethod
    def resolve_return_policies(
        _root, info, seller_id=None, product_id=None, is_active=None, **kwargs
    ):
        from .types import ReturnPolicyCountableConnection

        qs = resolve_return_policies(
            info, seller_id=seller_id, product_id=product_id, is_active=is_active
        )
        return create_connection_slice(qs, info, kwargs, ReturnPolicyCountableConnection)
