"""GraphQL mutation for tracking product views."""

from typing import TYPE_CHECKING
from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils import timezone

from ....core.tracing import traced_atomic_transaction
from ...core.context import get_database_connection_name
from ...core import ResolveInfo
from ...core.mutations import BaseMutation
from ...core.types import MarketplaceError
from ...core.utils import from_global_id_or_error
from saleor.marketplace import error_codes

if TYPE_CHECKING:
    from ....account.models import User


RECENTLY_VIEWED_METADATA_KEY = "recently_viewed_products"


class ProductView(BaseMutation):
    """Track a product view for the authenticated user."""

    class Meta:
        description = "Track a product view to add it to the user's recently viewed products."
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        """Track product view."""
        user = info.context.user
        if not user or not user.is_authenticated:
            raise ValidationError(
                {
                    "user": ValidationError(
                        "You must be authenticated to track product views.",
                        code=error_codes.MarketplaceErrorCode.INVALID.value,
                    )
                }
            )

        product_id = data.get("product_id")
        if not product_id:
            raise ValidationError(
                {
                    "productId": ValidationError(
                        "Product ID is required.",
                        code=error_codes.MarketplaceErrorCode.REQUIRED.value,
                    )
                }
            )

        # Resolve product ID
        from ...product.types import Product

        _, product_pk = from_global_id_or_error(product_id, Product)

        # Verify product exists
        connection_name = get_database_connection_name(info.context)
        from ....product import models as product_models

        try:
            product = product_models.Product.objects.using(connection_name).get(
                pk=product_pk
            )
        except product_models.Product.DoesNotExist:
            raise ValidationError(
                {
                    "productId": ValidationError(
                        "Product not found.",
                        code=error_codes.MarketplaceErrorCode.NOT_FOUND.value,
                    )
                }
            )

        # Get user preferences for limit
        preferences = user.get_value_from_metadata("preferences", {})
        limit = preferences.get("recently_viewed_products_limit", 10)

        # Get current recently viewed list
        recently_viewed = user.get_value_from_metadata(
            RECENTLY_VIEWED_METADATA_KEY, []
        )
        if not isinstance(recently_viewed, list):
            recently_viewed = []

        # Convert product ID to string for comparison
        product_id_str = str(product.id)

        # Remove existing entry if present (to move to front)
        recently_viewed = [
            item for item in recently_viewed if item.get("product_id") != product_id_str
        ]

        # Add product to front of list with timestamp
        recently_viewed.insert(
            0,
            {
                "product_id": product_id_str,
                "viewed_at": timezone.now().isoformat(),
            },
        )

        # Limit to user's preference (default 10)
        if limit > 0:
            recently_viewed = recently_viewed[:limit]

        # Save to metadata
        with traced_atomic_transaction():
            user.store_value_in_metadata(
                {RECENTLY_VIEWED_METADATA_KEY: recently_viewed}
            )
            user.save(update_fields=["metadata", "updated_at"])

        return cls.success_response()

