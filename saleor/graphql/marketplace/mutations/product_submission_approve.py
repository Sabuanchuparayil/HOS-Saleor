"""Mutation for approving/rejecting product submissions."""

import graphene

from ...core.doc_category import DOC_CATEGORY_MARKETPLACE
from ...core.mutations import BaseMutation
from ...core.types import MarketplaceError
from saleor.marketplace import models
from ...permission.enums import MarketplacePermissions
from ..enums import ProductApprovalStatusEnum
from ..types import ProductSubmission


class ProductSubmissionApprove(BaseMutation):
    """Approve or reject a product submission."""

    class Arguments:
        id = graphene.ID(required=True, description="ID of the product submission.")
        status = ProductApprovalStatusEnum(
            required=True, description="New approval status (approved, rejected, requires_revision)."
        )
        admin_notes = graphene.String(description="Admin notes on the decision.")

    product_submission = graphene.Field(ProductSubmission, description="The updated product submission.")

    class Meta:
        description = "Approve or reject a product submission."
        doc_category = DOC_CATEGORY_MARKETPLACE
        permissions = (MarketplacePermissions.MANAGE_CATALOG,)
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(cls, _root, info, id, status, admin_notes=None):
        """Approve or reject product submission."""
        product_submission = cls.get_node_or_error(
            info, id, only_type=ProductSubmission, field="id"
        )

        # Update status - convert enum value to model value
        from saleor.marketplace.models import ProductApprovalStatus
        status_value = status.value if hasattr(status, 'value') else status
        
        product_submission.status = status_value
        product_submission.admin_notes = admin_notes
        product_submission.reviewed_by = info.context.user
        from django.utils import timezone
        product_submission.reviewed_at = timezone.now()
        product_submission.save(update_fields=["status", "admin_notes", "reviewed_by", "reviewed_at"])

        # Update product approval status
        product_submission.product.approval_status = status_value
        product_submission.product.save(update_fields=["approval_status"])

        return cls(product_submission=product_submission)

