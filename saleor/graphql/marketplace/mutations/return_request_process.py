"""Mutation for processing return requests."""

import graphene

from ...core.doc_category import DOC_CATEGORY_MARKETPLACE
from ...core.mutations import BaseMutation
from ...core.types import MarketplaceError
from saleor.marketplace import models
from saleor.marketplace.models import ReturnRequestStatus
from saleor.permission.enums import MarketplacePermissions
from ..enums import ReturnRequestStatusEnum
from ..types import ReturnRequest


class ReturnRequestProcess(BaseMutation):
    """Process a return request (approve, reject, or update status)."""

    class Arguments:
        id = graphene.ID(required=True, description="ID of the return request.")
        status = ReturnRequestStatusEnum(
            required=True, description="New status (approved, rejected, processing, completed, cancelled)."
        )

    return_request = graphene.Field(ReturnRequest, description="The updated return request.")

    class Meta:
        description = "Process a return request (approve, reject, or update status)."
        doc_category = DOC_CATEGORY_MARKETPLACE
        permissions = (MarketplacePermissions.MANAGE_FULFILLMENT,)
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(cls, _root, info, id, status):
        """Process return request."""
        return_request = cls.get_node_or_error(
            info, id, only_type=ReturnRequest, field="id"
        )

        # Convert enum value to model value
        status_value = status.value if hasattr(status, 'value') else status

        # Update status
        return_request.status = status_value
        return_request.processed_by = info.context.user
        from django.utils import timezone
        return_request.processed_at = timezone.now()
        return_request.save(update_fields=["status", "processed_by", "processed_at"])

        return cls(return_request=return_request)


