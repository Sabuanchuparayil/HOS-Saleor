"""Mutation for processing return requests."""

import graphene
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from ...core.doc_category import DOC_CATEGORY_MARKETPLACE
from ...core.mutations import BaseMutation
from ...core.types import MarketplaceError
from ...core.context import get_database_connection_name
from saleor.marketplace import models
from saleor.marketplace.models import ReturnRequestStatus
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
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(cls, _root, info, id, status):
        """Process return request."""
        return_request = cls.get_node_or_error(
            info, id, only_type=ReturnRequest, field="id"
        )

        # Permissions:
        # - staff/app: allowed
        # - seller owner/staff: allowed for their own order line's seller
        from saleor.permission.auth_filters import is_app, is_staff_user

        if not (is_app(info.context) or is_staff_user(info.context)):
            user = info.context.user
            if not user or not user.is_authenticated:
                raise PermissionDenied("Authentication required.")

            connection_name = get_database_connection_name(info.context)
            seller_ids = (
                models.Seller.objects.using(connection_name)
                .filter(Q(owner=user) | Q(staff=user))
                .values_list("id", flat=True)
            )

            line_seller_id = getattr(return_request.order_line, "seller_id", None)
            if not line_seller_id or line_seller_id not in set(seller_ids):
                raise PermissionDenied("You can only process return requests for your own orders.")

        # Convert enum value to model value
        status_value = status.value if hasattr(status, 'value') else status

        # Update status
        return_request.status = status_value
        return_request.processed_by = info.context.user
        from django.utils import timezone
        return_request.processed_at = timezone.now()
        return_request.save(update_fields=["status", "processed_by", "processed_at"])

        return cls(return_request=return_request)


