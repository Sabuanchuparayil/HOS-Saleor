"""Mutation for sellers to create products with approval workflow."""

import graphene
from django.core.exceptions import PermissionDenied, ValidationError

from ...core.doc_category import DOC_CATEGORY_MARKETPLACE
from ...core.mutations import BaseMutation
from ...core.types import MarketplaceError
from saleor.marketplace import models
from saleor.marketplace.context import get_seller_from_context
from ...permission.enums import MarketplacePermissions
from ....product import models as product_models
from ....graphql.product.mutations.product.product_create import (
    ProductCreate,
    ProductCreateInput,
)
from ....graphql.product.types import Product
from ....graphql.utils import get_user_or_app_from_context
from ..types import ProductSubmission


class SellerProductCreateInput(ProductCreateInput):
    """Input for seller product creation (extends ProductCreateInput)."""

    class Meta:
        doc_category = DOC_CATEGORY_MARKETPLACE


class SellerProductCreate(BaseMutation):
    """Create a product as a seller (requires admin approval)."""

    class Arguments:
        input = SellerProductCreateInput(
            required=True, description="Fields required to create a product."
        )

    product = graphene.Field(Product, description="The created product.")
    product_submission = graphene.Field(
        ProductSubmission, description="The product submission record."
    )

    class Meta:
        description = "Create a product as a seller (requires admin approval)."
        doc_category = DOC_CATEGORY_MARKETPLACE
        permissions = (MarketplacePermissions.MANAGE_CATALOG,)
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(cls, _root, info, input):
        """Create product and product submission."""
        from ....core.tracing import traced_atomic_transaction
        from ....graphql.core.context import ChannelContext
        from ....graphql.product.mutations.product.product_create import (
            ProductCreate,
        )
        from ....graphql.product.mutations.product import product_cleaner as cleaner
        from ....graphql.attribute.utils.attribute_assignment import (
            AttributeAssignmentMixin,
        )
        from ....graphql.core.validators import clean_seo_fields
        from ....graphql.product.mutations.product.utils import clean_tax_code
        from ....graphql.plugins.dataloaders import get_plugin_manager_promise

        # Get seller from context or check if user owns a seller
        seller = get_seller_from_context(info.context)
        user_or_app = get_user_or_app_from_context(info.context)

        if not seller and user_or_app:
            # Try to find seller owned by this user
            seller = models.Seller.objects.filter(owner=user_or_app).first()

        if not seller:
            raise PermissionDenied(
                permissions=[MarketplacePermissions.MANAGE_CATALOG],
                message="You must be a seller to create products.",
            )

        # Check if seller is active
        if seller.status != models.SellerStatus.ACTIVE:
            raise ValidationError(
                {
                    "seller": ValidationError(
                        "Your seller account must be active to create products.",
                        code="INVALID",
                    )
                }
            )

        with traced_atomic_transaction():
            # Clean input using ProductCreate's clean_input
            cleaned_input = ProductCreate.clean_input(
                cls, info, None, input, **{"input": input}
            )

            # Create product instance
            product = product_models.Product()
            for field, value in cleaned_input.items():
                if field not in ("attributes", "collections", "product_type"):
                    setattr(product, field, value)

            # Set seller-specific fields
            product.seller = seller
            product.approval_status = models.ProductApprovalStatus.PENDING
            product.is_exclusive_to_seller = True

            # Save product
            product.search_index_dirty = True
            product.save()

            # Save attributes
            attributes = cleaned_input.get("attributes")
            if attributes:
                AttributeAssignmentMixin.save(product, attributes)

            # Save collections
            collections = cleaned_input.get("collections")
            if collections is not None:
                product.collections.set(collections)

            # Create ProductSubmission
            product_submission = models.ProductSubmission.objects.create(
                seller=seller,
                product=product,
                status=models.ProductApprovalStatus.PENDING,
            )

            # Post-save actions (trigger events)
            manager = get_plugin_manager_promise(info.context).get()
            ProductCreate.call_event(manager.product_created, product)

            # Wrap product in ChannelContext
            product_context = ChannelContext(node=product, channel_slug=None)

            return cls(
                product=product_context,
                product_submission=product_submission,
            )

