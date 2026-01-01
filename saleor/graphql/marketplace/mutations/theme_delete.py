"""GraphQL mutation for deleting a theme."""

import graphene

from ....core.tracing import traced_atomic_transaction
from saleor.marketplace import models
from ....permission.enums import MarketplacePermissions
from ...core import ResolveInfo
from ...core.mutations import ModelDeleteMutation, ModelWithExtRefMutation
from ...core.types import MarketplaceError
from ..types import Theme


class ThemeDelete(ModelDeleteMutation, ModelWithExtRefMutation):
    """Delete a theme."""

    class Arguments:
        id = graphene.ID(required=False, description="ID of a theme to delete.")
        external_reference = graphene.String(
            required=False, description="External ID of a theme to delete."
        )

    class Meta:
        description = "Deletes a theme template."
        model = models.Theme
        object_type = Theme
        permissions = (MarketplacePermissions.MANAGE_SELLERS,)
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(  # type: ignore[override]
        cls, _root, info: ResolveInfo, /, *, external_reference=None, id=None
    ):
        instance = cls.get_instance(info, external_reference=external_reference, id=id)
        db_id = instance.id
        with traced_atomic_transaction():
            instance.delete()
            instance.id = db_id
        return cls.success_response(instance)

