"""GraphQL resolvers for marketplace."""

from datetime import date
from decimal import Decimal
from typing import Optional

import graphene
from django.db.models import Q, Sum
from django.utils import timezone

from ..core import ResolveInfo
from ..core.context import get_database_connection_name
from ..core.enums import ReportingPeriod
from prices import Money
from ..core.utils import from_global_id_or_error
from ..utils.filters import reporting_period_to_date
from saleor.marketplace import models
from saleor.marketplace.context import get_seller_from_context
from saleor.marketplace.dataloaders import SellerByDomainLoader, SellerByIdLoader, SellerBySlugLoader
from saleor.marketplace.utils import (
    calculate_seller_earnings_total,
    calculate_seller_revenue,
    get_seller_order_count,
)
from ..core.validators import validate_one_of_args_is_in_query
from ...product import models as product_models
from ..product.resolvers import resolve_collections
from ...utils import get_user_or_app_from_context
from .types import NewsletterSubscription, Seller, SellerAnalytics, Theme, UserPreferences


def resolve_seller(info: ResolveInfo, id: str | None, slug: str | None):
    """Resolve a seller by ID or slug."""
    validate_one_of_args_is_in_query("id", id, "slug", slug)

    qs = models.Seller.objects.using(get_database_connection_name(info.context)).all()
    
    # Apply tenant filtering
    current_seller = get_seller_from_context(info.context)
    if current_seller:
        qs = qs.filter(id=current_seller.id)

    if id:
        _, db_id = from_global_id_or_error(id, Seller)
        return qs.filter(id=db_id).first()

    if slug:
        return qs.filter(slug=slug).first()

    return None


def resolve_sellers(info: ResolveInfo):
    """Resolve all sellers, filtered by current tenant if applicable."""
    qs = models.Seller.objects.using(
        get_database_connection_name(info.context)
    ).all()
    
    # If there's a seller in context (from domain routing), filter to that seller only
    # This enables tenant isolation for seller-specific storefronts
    context_seller = get_seller_from_context(info.context)
    if context_seller:
        # For seller-specific storefronts, only show the current seller
        qs = qs.filter(id=context_seller.id)
        
    return qs


def resolve_seller_analytics(
      info: ResolveInfo, seller: models.Seller, period: Optional[ReportingPeriod] = None
  ) -> SellerAnalytics:
      """Resolve analytics data for a given seller."""
      start_date = None
      if period:
          start_date = reporting_period_to_date(period)

      revenue = calculate_seller_revenue(seller, start_date=start_date)
      earnings = calculate_seller_earnings_total(seller, start_date=start_date)
      order_count = get_seller_order_count(seller, start_date=start_date)
      # Calculate platform fee total as revenue - earnings
      platform_fee_total = revenue - earnings

      currency = seller.channel.currency_code if seller.channel else "USD" # Default currency

      return SellerAnalytics(
          revenue=Money(revenue, currency),
          earnings=Money(earnings, currency),
          order_count=order_count,
          platform_fee_total=Money(platform_fee_total, currency),
      )


def resolve_theme(info: ResolveInfo, id: str | None, slug: str | None):
    """Resolve a theme by ID or slug."""
    validate_one_of_args_is_in_query("id", id, "slug", slug)

    qs = models.Theme.objects.using(get_database_connection_name(info.context)).all()

    if id:
        _, db_id = from_global_id_or_error(id, Theme)
        return qs.filter(id=db_id).first()

    if slug:
        return qs.filter(slug=slug).first()

    return None


def resolve_themes(info: ResolveInfo, is_active: Optional[bool] = None):
    """Resolve all themes."""
    qs = models.Theme.objects.using(get_database_connection_name(info.context)).all()
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return qs


def resolve_default_theme(info: ResolveInfo):
    """Resolve the default theme."""
    return models.Theme.objects.using(get_database_connection_name(info.context)).filter(
        is_default=True, is_active=True
    ).first()


def resolve_newsletter_subscription(info: ResolveInfo, id: str | None, email: str | None):
    """Resolve a newsletter subscription by ID or email."""
    validate_one_of_args_is_in_query("id", id, "email", email)

    qs = models.NewsletterSubscription.objects.using(
        get_database_connection_name(info.context)
    ).all()

    if id:
        _, db_id = from_global_id_or_error(id, NewsletterSubscription)
        return qs.filter(id=db_id).first()

    if email:
        return qs.filter(email=email).first()

    return None


def resolve_newsletter_subscriptions(info: ResolveInfo, is_active: Optional[bool] = None):
    """Resolve all newsletter subscriptions."""
    qs = models.NewsletterSubscription.objects.using(
        get_database_connection_name(info.context)
    ).all()
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return qs


def resolve_user_preferences(info: ResolveInfo) -> Optional[UserPreferences]:
    """Resolve user preferences from the authenticated user's metadata."""
    user = info.context.user
    if not user.is_authenticated:
        return None

    preferences_data = user.get_value_from_metadata("preferences", {})
    return UserPreferences(**preferences_data)


def resolve_featured_collections(
    info: ResolveInfo,
    channel: Optional[str] = None,
    first: Optional[int] = None,
):
    """Resolve featured collections for homepage.
    
    Collections are marked as featured via metadata key 'is_featured' = True.
    """
    from ...product import models as product_models
    
    connection_name = get_database_connection_name(info.context)
    requestor = get_user_or_app_from_context(info.context)
    
    # Get collections marked as featured in metadata
    collections = product_models.Collection.objects.using(connection_name).filter(
        metadata__contains={"is_featured": True}
    )
    
    # Filter by channel if provided
    if channel:
        # Filter to only published collections in this channel
        published_collections = product_models.CollectionChannelListing.objects.using(
            connection_name
        ).filter(
            channel__slug=channel,
            is_published=True,
        ).values_list("collection_id", flat=True)
        collections = collections.filter(id__in=published_collections)
    
    # Apply visibility filtering (respects published/unpublished)
    collections = collections.visible_to_user(requestor, channel)
    
    # Limit results
    if first:
        collections = collections[:first]
    
    return list(collections)


def resolve_featured_products(
    info: ResolveInfo,
    channel: Optional[str] = None,
    first: Optional[int] = None,
):
    """Resolve featured products for homepage.
    
    Products are marked as featured via metadata key 'is_featured' = True,
    OR they belong to a featured collection.
    """
    from ...product import models as product_models
    
    connection_name = get_database_connection_name(info.context)
    requestor = get_user_or_app_from_context(info.context)
    
    # Get products marked as featured in metadata
    featured_products = product_models.Product.objects.using(connection_name).filter(
        metadata__contains={"is_featured": True}
    )
    
    # Also get products from featured collections
    featured_collection_ids = product_models.Collection.objects.using(connection_name).filter(
        metadata__contains={"is_featured": True}
    ).values_list("id", flat=True)
    
    if featured_collection_ids:
        products_from_collections = product_models.Product.objects.using(connection_name).filter(
            collections__id__in=featured_collection_ids
        )
        # Combine both querysets
        featured_products = (featured_products | products_from_collections).distinct()
    
    # Filter by channel if provided
    if channel:
        # Filter to only published products in this channel
        published_products = product_models.ProductChannelListing.objects.using(
            connection_name
        ).filter(
            channel__slug=channel,
            is_published=True,
        ).values_list("product_id", flat=True)
        featured_products = featured_products.filter(id__in=published_products)
    
    # Apply visibility filtering
    featured_products = featured_products.visible_to_user(requestor, channel)
    
    # Limit results
    if first:
        featured_products = featured_products[:first]
    
    return list(featured_products)


def resolve_recently_viewed_products(
    info: ResolveInfo,
    channel: Optional[str] = None,
    first: Optional[int] = None,
):
    """Resolve recently viewed products for the authenticated user."""
    from ...product import models as product_models
    from ...utils import get_user_or_app_from_context
    
    user = info.context.user
    if not user or not user.is_authenticated:
        return []
    
    connection_name = get_database_connection_name(info.context)
    requestor = get_user_or_app_from_context(info.context)
    
    # Get recently viewed product IDs from metadata
    recently_viewed = user.get_value_from_metadata("recently_viewed_products", [])
    if not isinstance(recently_viewed, list) or not recently_viewed:
        return []
    
    # Extract product IDs (handle both UUID strings and dict format)
    product_ids = []
    for item in recently_viewed:
        if isinstance(item, dict):
            product_id_str = item.get("product_id")
            if product_id_str:
                try:
                    from uuid import UUID
                    product_ids.append(UUID(product_id_str))
                except (ValueError, TypeError):
                    continue
        elif isinstance(item, str):
            try:
                from uuid import UUID
                product_ids.append(UUID(item))
            except (ValueError, TypeError):
                continue
    
    if not product_ids:
        return []
    
    # Get products
    products = product_models.Product.objects.using(connection_name).filter(
        id__in=product_ids
    )
    
    # Filter by channel if provided
    if channel:
        # Filter to only published products in this channel
        published_products = product_models.ProductChannelListing.objects.using(
            connection_name
        ).filter(
            channel__slug=channel,
            is_published=True,
        ).values_list("product_id", flat=True)
        products = products.filter(id__in=published_products)
    
    # Apply visibility filtering
    products = products.visible_to_user(requestor, channel)
    
    # Maintain order from recently_viewed list
    product_map = {str(product.id): product for product in products}
    ordered_products = []
    for item in recently_viewed:
        if isinstance(item, dict):
            product_id_str = item.get("product_id")
        elif isinstance(item, str):
            product_id_str = item
        else:
            continue
        
        if product_id_str in product_map:
            ordered_products.append(product_map[product_id_str])
            # Remove from map to avoid duplicates
            del product_map[product_id_str]
    
    # Limit results
    if first:
        ordered_products = ordered_products[:first]
    
    return ordered_products


def resolve_fulfillment_centers(info: ResolveInfo, is_active: Optional[bool] = None):
    """Resolve all fulfillment centers."""
    qs = models.FulfillmentCenter.objects.using(
        get_database_connection_name(info.context)
    ).all()
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return qs.order_by("priority", "name")


def resolve_fulfillment_center(info: ResolveInfo, id: str):
    """Resolve a fulfillment center by ID."""
    from .types import FulfillmentCenter
    _, db_id = from_global_id_or_error(id, FulfillmentCenter)
    return models.FulfillmentCenter.objects.using(
        get_database_connection_name(info.context)
    ).filter(id=db_id).first()


def resolve_product_submissions(
    info: ResolveInfo,
    seller_id: Optional[str] = None,
    status: Optional[str] = None,
):
    """Resolve product submissions, optionally filtered by seller and status."""
    qs = models.ProductSubmission.objects.using(
        get_database_connection_name(info.context)
    ).all()

    if seller_id:
        from .types import Seller
        _, seller_pk = from_global_id_or_error(seller_id, Seller)
        qs = qs.filter(seller_id=seller_pk)

    if status:
        qs = qs.filter(status=status)

    return qs.order_by("-submitted_at")


def resolve_product_submission(info: ResolveInfo, id: str):
    """Resolve a product submission by ID."""
    from .types import ProductSubmission
    _, db_id = from_global_id_or_error(id, ProductSubmission)
    return models.ProductSubmission.objects.using(
        get_database_connection_name(info.context)
    ).filter(id=db_id).first()


def resolve_return_requests(
    info: ResolveInfo,
    order_id: Optional[str] = None,
    status: Optional[str] = None,
):
    """Resolve return requests, optionally filtered by order and status."""
    from ...utils import get_user_or_app_from_context
    from saleor.permission.auth_filters import is_app, is_staff_user

    qs = models.ReturnRequest.objects.using(
        get_database_connection_name(info.context)
    ).all()

    # Users can only see their own return requests (unless staff/app)
    user = info.context.user
    requestor = get_user_or_app_from_context(info.context)
    # Apps and staff users can see all return requests
    is_staff_or_app = is_app(info.context) or is_staff_user(info.context)
    if user and user.is_authenticated and not is_staff_or_app:
        qs = qs.filter(user=user)

    if order_id:
        from ..order.types import Order
        _, order_pk = from_global_id_or_error(order_id, Order)
        qs = qs.filter(order_id=order_pk)

    if status:
        qs = qs.filter(status=status)

    return qs.order_by("-requested_at")


def resolve_return_request(info: ResolveInfo, id: str):
    """Resolve a return request by ID."""
    from .types import ReturnRequest
    from ...utils import get_user_or_app_from_context
    from saleor.permission.auth_filters import is_app, is_staff_user

    _, db_id = from_global_id_or_error(id, ReturnRequest)
    return_request = models.ReturnRequest.objects.using(
        get_database_connection_name(info.context)
    ).filter(id=db_id).first()

    if return_request:
        # Check permissions
        user = info.context.user
        requestor = get_user_or_app_from_context(info.context)
        # Apps and staff users can see any return request
        is_staff_or_app = is_app(info.context) or is_staff_user(info.context)
        if user and user.is_authenticated:
            if not is_staff_or_app and return_request.user_id != user.id:
                return None

    return return_request


def resolve_seller_orders(info: ResolveInfo, seller_id: str):
    """Resolve orders for a specific seller."""
    from ...utils import get_user_or_app_from_context
    from ...order import models as order_models
    from .types import Seller
    
    _, seller_pk = from_global_id_or_error(seller_id, Seller)
    connection_name = get_database_connection_name(info.context)
    requestor = get_user_or_app_from_context(info.context)
    
    # Get orders that have lines belonging to this seller
    qs = order_models.Order.objects.using(connection_name).non_draft().filter(
        lines__seller_id=seller_pk
    ).distinct()
    
    # Permission check: sellers can only see their own orders, staff/app can see all
    from saleor.permission.auth_filters import is_app, is_staff_user
    is_staff_or_app = is_app(info.context) or is_staff_user(info.context)
    if not is_staff_or_app:
        # Check if requestor is the seller owner
        seller = models.Seller.objects.using(connection_name).filter(id=seller_pk).first()
        if seller and seller.owner_id != requestor.id:
            # Not the seller owner and not staff/app - return empty queryset
            return order_models.Order.objects.using(connection_name).none()
    
    return qs.order_by("-created_at")


def resolve_seller_settlements(
    info: ResolveInfo, seller_id: str, status: Optional[str] = None
):
    """Resolve settlements for a specific seller."""
    from .types import Seller
    from ...utils import get_user_or_app_from_context
    
    _, seller_pk = from_global_id_or_error(seller_id, Seller)
    connection_name = get_database_connection_name(info.context)
    requestor = get_user_or_app_from_context(info.context)
    
    qs = models.SellerSettlement.objects.using(connection_name).filter(
        seller_id=seller_pk
    )
    
    # Permission check: sellers can only see their own settlements, staff/app can see all
    from saleor.permission.auth_filters import is_app, is_staff_user
    is_staff_or_app = is_app(info.context) or is_staff_user(info.context)
    if not is_staff_or_app:
        seller = models.Seller.objects.using(connection_name).filter(id=seller_pk).first()
        if seller and seller.owner_id != requestor.id:
            # Not the seller owner and not staff/app - return empty queryset
            return models.SellerSettlement.objects.using(connection_name).none()
    
    if status:
        qs = qs.filter(status=status)
    
    return qs.order_by("-created_at")
