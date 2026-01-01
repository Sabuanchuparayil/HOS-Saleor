from functools import partial

import graphql
from django.urls import reverse
from django.utils.functional import SimpleLazyObject
from graphql import (
    GraphQLCachedBackend,
    GraphQLCoreBackend,
    GraphQLScalarType,
    GraphQLSchema,
    execute,
    parse,
    validate,
)
from graphql.backend.base import GraphQLDocument
from graphql.execution import ExecutionResult

from ..core.utils.cache import CacheDict
from ..graphql.notifications.schema import ExternalNotificationMutations
from .account.schema import AccountMutations, AccountQueries
from .app.schema import AppMutations, AppQueries
from .attribute.schema import AttributeMutations, AttributeQueries
from .attribute.types import ASSIGNED_ATTRIBUTE_TYPES
from .channel.schema import ChannelMutations, ChannelQueries
from .checkout.schema import CheckoutMutations, CheckoutQueries
from .core.enums import unit_enums
from .core.federation.schema import build_federated_schema
from .core.schema import CoreMutations, CoreQueries
from .csv.schema import CsvMutations, CsvQueries
from .discount.schema import DiscountMutations, DiscountQueries
from .giftcard.schema import GiftCardMutations, GiftCardQueries
from .invoice.schema import InvoiceMutations
# #region agent log
import json
import os
import sys
import time
log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".cursor", "debug.log")
def debug_log(location, message, data=None, hypothesis_id=None):
    """Log debug information to both file and stdout for Railway visibility."""
    log_entry = {"location": location, "message": message, "timestamp": time.time(), "sessionId": "debug-session", "runId": "run1"}
    if data:
        log_entry["data"] = data
    if hypothesis_id:
        log_entry["hypothesisId"] = hypothesis_id
    log_str = json.dumps(log_entry)
    # Write to file
    try:
        with open(log_path, "a") as f:
            f.write(log_str + "\n")
    except Exception:
        pass
    # Also write to stdout for Railway logs
    print(f"[DEBUG] {log_str}", file=sys.stderr)
try:
    debug_log("api.py:33", "About to import marketplace schema", hypothesis_id="A")
except Exception:
    pass
# #endregion
try:
    from .marketplace import schema as marketplace_schema
    # #region agent log
    try:
        debug_log("api.py:43", "Marketplace schema imported successfully", {"hasHomepageQueries": hasattr(marketplace_schema, "HomepageQueries"), "hasSellerQueries": hasattr(marketplace_schema, "SellerQueries")}, hypothesis_id="A")
    except Exception:
        pass
    # #endregion
except ImportError as e:
    # #region agent log
    try:
        debug_log("api.py:43", "Failed to import marketplace schema", {"error": str(e), "errorType": type(e).__name__}, hypothesis_id="D")
    except Exception:
        pass
    # #endregion
    raise
except Exception as e:
    # #region agent log
    try:
        debug_log("api.py:43", "Unexpected error importing marketplace schema", {"error": str(e), "errorType": type(e).__name__}, hypothesis_id="E")
    except Exception:
        pass
    # #endregion
    raise
# #endregion
from .menu.schema import MenuMutations, MenuQueries
from .meta.schema import MetaMutations
from .order.schema import OrderMutations, OrderQueries
from .page.schema import PageMutations, PageQueries
from .payment.schema import PAYMENT_ADDITIONAL_TYPES, PaymentMutations, PaymentQueries
from .plugins.schema import PluginsMutations, PluginsQueries
from .product.schema import ProductMutations, ProductQueries
from .shipping.schema import ShippingMutations, ShippingQueries
from .shop.schema import ShopMutations, ShopQueries
from .tax.schema import TaxMutations, TaxQueries
from .translations.schema import TranslationQueries
from .warehouse.schema import (
    StockMutations,
    StockQueries,
    WarehouseMutations,
    WarehouseQueries,
)
from .webhook.schema import WebhookMutations, WebhookQueries
from .webhook.subscription_types import WEBHOOK_TYPES_MAP, Subscription

API_PATH = SimpleLazyObject(lambda: reverse("api"))


class Query(
    AccountQueries,
    AppQueries,
    AttributeQueries,
    ChannelQueries,
    CheckoutQueries,
    CoreQueries,
    CsvQueries,
    DiscountQueries,
    PluginsQueries,
    GiftCardQueries,
    MenuQueries,
    marketplace_schema.SellerQueries,
    marketplace_schema.ThemeQueries,
    marketplace_schema.NewsletterQueries,
    marketplace_schema.UserPreferencesQueries,
    marketplace_schema.HomepageQueries,
    marketplace_schema.FulfillmentCenterQueries,
    marketplace_schema.ProductSubmissionQueries,
    marketplace_schema.SellerShippingMethodQueries,
    marketplace_schema.InventorySyncQueries,
    marketplace_schema.ReturnRequestQueries,
    marketplace_schema.LoyaltyPointsBalanceQueries,
    marketplace_schema.LoyaltyPointsTransactionQueries,
    marketplace_schema.BadgeQueries,
    marketplace_schema.UserBadgeQueries,
    marketplace_schema.RewardQueries,
    marketplace_schema.RewardRedemptionQueries,
    OrderQueries,
    PageQueries,
    PaymentQueries,
    ProductQueries,
    ShippingQueries,
    ShopQueries,
    StockQueries,
    TaxQueries,
    TranslationQueries,
    WarehouseQueries,
    WebhookQueries,
):
    pass


class Mutation(
    AccountMutations,
    AppMutations,
    AttributeMutations,
    ChannelMutations,
    CheckoutMutations,
    CoreMutations,
    CsvMutations,
    DiscountMutations,
    ExternalNotificationMutations,
    PluginsMutations,
    GiftCardMutations,
    InvoiceMutations,
    MenuMutations,
    MetaMutations,
    marketplace_schema.SellerMutations,
    marketplace_schema.ThemeMutations,
    marketplace_schema.NewsletterMutations,
    marketplace_schema.UserPreferencesMutations,
    marketplace_schema.LoyaltyMutations,
    OrderMutations,
    PageMutations,
    PaymentMutations,
    ProductMutations,
    ShippingMutations,
    ShopMutations,
    StockMutations,
    TaxMutations,
    WarehouseMutations,
    WebhookMutations,
):
    pass


GraphQLDocDirective = graphql.GraphQLDirective(
    name="doc",
    description="Groups fields and operations into named groups.",
    args={
        "category": graphql.GraphQLArgument(
            type_=graphql.GraphQLNonNull(graphql.GraphQLString),
            description="Name of the grouping category",
        )
    },
    locations=[
        graphql.DirectiveLocation.ENUM,
        graphql.DirectiveLocation.FIELD,
        graphql.DirectiveLocation.FIELD_DEFINITION,
        graphql.DirectiveLocation.INPUT_OBJECT,
        graphql.DirectiveLocation.OBJECT,
        graphql.DirectiveLocation.INTERFACE,
    ],
)


def serialize_webhook_event(value):
    return value


GraphQLWebhookEventAsyncType = GraphQLScalarType(
    name="WebhookEventTypeAsyncEnum",
    description="",
    serialize=serialize_webhook_event,
)

GraphQLWebhookEventSyncType = GraphQLScalarType(
    name="WebhookEventTypeSyncEnum",
    description="",
    serialize=serialize_webhook_event,
)

GraphQLWebhookEventsInfoDirective = graphql.GraphQLDirective(
    name="webhookEventsInfo",
    description="Webhook events triggered by a specific location.",
    args={
        "asyncEvents": graphql.GraphQLArgument(
            type_=graphql.GraphQLNonNull(
                graphql.GraphQLList(
                    graphql.GraphQLNonNull(GraphQLWebhookEventAsyncType)
                )
            ),
            description=(
                "List of asynchronous webhook events triggered by a specific location."
            ),
        ),
        "syncEvents": graphql.GraphQLArgument(
            type_=graphql.GraphQLNonNull(
                graphql.GraphQLList(graphql.GraphQLNonNull(GraphQLWebhookEventSyncType))
            ),
            description=(
                "List of synchronous webhook events triggered by a specific location."
            ),
        ),
    },
    locations=[
        graphql.DirectiveLocation.FIELD,
        graphql.DirectiveLocation.FIELD_DEFINITION,
        graphql.DirectiveLocation.INPUT_OBJECT,
        graphql.DirectiveLocation.OBJECT,
    ],
)
# #region agent log
try:
    import graphene
    # Get all attributes from Query class
    query_attrs = dir(Query)
    # Check for graphene Field instances
    query_fields = []
    for attr in query_attrs:
        if attr.startswith("_"):
            continue
        attr_value = getattr(Query, attr, None)
        if isinstance(attr_value, (graphene.Field, ConnectionField, BaseField)):
            query_fields.append(attr)
    
    query_bases = [base.__name__ for base in Query.__bases__]
    has_homepage = "HomepageQueries" in query_bases
    has_seller = "SellerQueries" in query_bases
    
    # Check if fields exist directly on Query class
    has_featured_products_field = hasattr(Query, "featured_products")
    has_sellers_field = hasattr(Query, "sellers")
    has_featured_collections_field = hasattr(Query, "featured_collections")
    
    # Check _meta.fields if available (Graphene stores fields here)
    meta_fields = []
    if hasattr(Query, "_meta") and hasattr(Query._meta, "fields"):
        meta_fields = list(Query._meta.fields.keys()) if Query._meta.fields else []
    
    # Check if HomepageQueries and SellerQueries have their fields
    homepage_fields = []
    seller_fields = []
    if hasattr(marketplace_schema, "HomepageQueries"):
        hq = marketplace_schema.HomepageQueries
        homepage_fields = [attr for attr in dir(hq) if not attr.startswith("_") and isinstance(getattr(hq, attr, None), (graphene.Field, ConnectionField, BaseField))]
    if hasattr(marketplace_schema, "SellerQueries"):
        sq = marketplace_schema.SellerQueries
        seller_fields = [attr for attr in dir(sq) if not attr.startswith("_") and isinstance(getattr(sq, attr, None), (graphene.Field, ConnectionField, BaseField))]
    
    debug_log("api.py:251", "About to build schema", {
        "queryClass": Query.__name__,
        "queryBases": query_bases,
        "hasHomepageQueriesInQuery": has_homepage,
        "hasSellerQueriesInQuery": has_seller,
        "hasFeaturedProductsField": has_featured_products_field,
        "hasSellersField": has_sellers_field,
        "hasFeaturedCollectionsField": has_featured_collections_field,
        "metaFields": meta_fields[:30],
        "queryFieldsCount": len(query_fields),
        "queryFieldsSample": query_fields[:20],
        "homepageQueriesFields": homepage_fields,
        "sellerQueriesFields": seller_fields
    }, hypothesis_id="B")
except Exception as e:
    try:
        import traceback
        debug_log("api.py:251", "Error checking Query class", {"error": str(e), "traceback": traceback.format_exc()}, hypothesis_id="B")
    except Exception:
        pass
# #endregion
# #region agent log
# Force Graphene to discover fields by accessing _meta before schema build
try:
    # This forces Graphene to initialize the Query class and discover fields
    if hasattr(Query, "_meta"):
        _ = Query._meta
    # Also try to access fields directly to ensure they're discovered
    if hasattr(Query, "featured_products"):
        _ = Query.featured_products
    if hasattr(Query, "sellers"):
        _ = Query.sellers
    debug_log("api.py:310", "Query class initialized, checking field discovery", {
        "hasMeta": hasattr(Query, "_meta"),
        "metaFieldsCount": len(Query._meta.fields) if hasattr(Query, "_meta") and hasattr(Query._meta, "fields") and Query._meta.fields else 0,
        "hasFeaturedProducts": hasattr(Query, "featured_products"),
        "hasSellers": hasattr(Query, "sellers"),
    }, hypothesis_id="F")
except Exception as e:
    try:
        import traceback
        debug_log("api.py:310", "Error during Query initialization", {"error": str(e), "traceback": traceback.format_exc()}, hypothesis_id="F")
    except Exception:
        pass
# #endregion
schema = build_federated_schema(
    Query,
    mutation=Mutation,
    types=(
        unit_enums
        + list(WEBHOOK_TYPES_MAP.values())
        + PAYMENT_ADDITIONAL_TYPES
        + ASSIGNED_ATTRIBUTE_TYPES
    ),
    subscription=Subscription,
    directives=graphql.specified_directives
    + [GraphQLDocDirective, GraphQLWebhookEventsInfoDirective],
)
# #region agent log
try:
    query_type = schema.get_type("Query")
    field_names = [field.name for field in query_type.fields.values()] if query_type and hasattr(query_type, "fields") else []
    has_sellers = "sellers" in field_names
    has_featured_products = "featuredProducts" in field_names
    has_featured_collections = "featuredCollections" in field_names
    debug_log("api.py:285", "Schema built", {"totalFields": len(field_names), "hasSellers": has_sellers, "hasFeaturedProducts": has_featured_products, "hasFeaturedCollections": has_featured_collections, "marketplaceFields": [f for f in field_names if "seller" in f.lower() or "featured" in f.lower()]}, hypothesis_id="C")
except Exception as e:
    try:
        debug_log("api.py:285", "Error checking schema", {"error": str(e)}, hypothesis_id="C")
    except Exception:
        pass
# #endregion


def _fail(errors, **_kwargs) -> ExecutionResult:
    return ExecutionResult(errors=errors, invalid=True)


class SaleorGraphQLBackend(GraphQLCoreBackend):
    def document_from_string(
        self,
        schema: GraphQLSchema,
        document_string: str,  # type: ignore[override]
    ) -> GraphQLDocument:
        # validate eagerly so we can cache the result
        document_ast = parse(document_string)
        validation_errors = validate(schema, document_ast)
        if validation_errors:
            return GraphQLDocument(
                schema=schema,
                document_string=document_string,
                document_ast=document_ast,
                execute=partial(_fail, validation_errors),
            )

        return GraphQLDocument(
            schema=schema,
            document_string=document_string,
            document_ast=document_ast,
            execute=partial(execute, schema, document_ast, **self.execute_params),  # type: ignore[arg-type]
        )


backend = GraphQLCachedBackend(SaleorGraphQLBackend(), cache_map=CacheDict(1000))
