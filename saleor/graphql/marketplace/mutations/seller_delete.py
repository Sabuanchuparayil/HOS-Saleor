"""GraphQL mutation for deleting a seller."""

import graphene

from saleor.marketplace import models
from ....permission.enums import MarketplacePermissions
from ...core.mutations import ModelDeleteMutation
from ...core.types import MarketplaceError
from ..types import Seller


class SellerDelete(ModelDeleteMutation):
    """Delete a seller."""

    class Arguments:
        id = graphene.ID(required=False, description="ID of a seller to delete.")
        external_reference = graphene.String(
            required=False,
            description="External ID of a seller to delete.",
        )

    class Meta:
        description = "Deletes a seller."
        model = models.Seller
        object_type = Seller
        permissions = (MarketplacePermissions.MANAGE_SELLERS,)
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"
