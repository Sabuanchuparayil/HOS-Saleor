"""Mutation for creating a return request."""

import graphene
from django.core.exceptions import ValidationError

from ...core.doc_category import DOC_CATEGORY_MARKETPLACE
from ...core.mutations import BaseMutation
from ...core.types import MarketplaceError
from saleor.marketplace import models
from saleor.marketplace.models import ReturnRequestStatus
from ..types import ReturnRequest


class ReturnRequestCreate(BaseMutation):
    """Create a return request for an order line."""

    class Arguments:
        order_id = graphene.ID(required=True, description="ID of the order.")
        order_line_id = graphene.ID(required=True, description="ID of the order line to return.")
        reason = graphene.String(required=True, description="Reason for return.")

    return_request = graphene.Field(ReturnRequest, description="The created return request.")

    class Meta:
        description = "Create a return request for an order line."
        doc_category = DOC_CATEGORY_MARKETPLACE
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(cls, _root, info, order_id, order_line_id, reason):
        """Create return request."""
        from ...graphql.order.types import Order, OrderLine

        order = cls.get_node_or_error(info, order_id, only_type=Order, field="order_id")
        order_line = cls.get_node_or_error(
            info, order_line_id, only_type=OrderLine, field="order_line_id"
        )

        # Verify order line belongs to order
        if order_line.order_id != order.id:
            raise ValidationError(
                {
                    "order_line_id": ValidationError(
                        "Order line does not belong to the specified order.",
                        code="INVALID",
                    )
                }
            )

        # Verify user owns the order
        user = info.context.user
        if not user or order.user_id != user.id:
            raise ValidationError(
                {
                    "order_id": ValidationError(
                        "You can only create return requests for your own orders.",
                        code="PERMISSION_DENIED",
                    )
                }
            )

        # Create return request
        return_request = models.ReturnRequest.objects.create(
            order=order,
            order_line=order_line,
            user=user,
            reason=reason,
            status=ReturnRequestStatus.PENDING,
        )

        return cls(return_request=return_request)

