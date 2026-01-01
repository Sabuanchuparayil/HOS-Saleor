"""GraphQL mutation for updating a theme."""

import graphene
from django.core.exceptions import ValidationError

from ....core.tracing import traced_atomic_transaction
from ...core.context import get_database_connection_name
from saleor.marketplace import models
from saleor.marketplace.error_codes import MarketplaceErrorCode
from ....permission.enums import MarketplacePermissions
from ...core import ResolveInfo
from ...core.mutations import ModelWithExtRefMutation
from ...core.types import MarketplaceError
from ...core.validators.file import clean_image_file
from ..inputs import ThemeUpdateInput
from ..types import Theme


class ThemeUpdate(ModelWithExtRefMutation):
    """Update an existing theme."""

    class Arguments:
        id = graphene.ID(required=False, description="ID of a theme to update.")
        external_reference = graphene.String(
            required=False, description="External ID of a theme to update."
        )
        input = ThemeUpdateInput(
            required=True, description="Fields required to update a theme."
        )

    class Meta:
        description = "Updates an existing theme template."
        model = models.Theme
        object_type = Theme
        permissions = (MarketplacePermissions.MANAGE_SELLERS,)
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"
        support_meta_field = True
        support_private_meta_field = True

    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)

        # Validate slug if changed
        if "slug" in cleaned_input and cleaned_input["slug"] != instance.slug:
            existing = models.Theme.objects.using(
                get_database_connection_name(info.context)
            ).filter(slug=cleaned_input["slug"]).exclude(pk=instance.pk)
            if existing.exists():
                raise ValidationError(
                    {
                        "slug": ValidationError(
                            "Theme with this slug already exists.",
                            code=MarketplaceErrorCode.UNIQUE.value,
                        )
                    }
                )

        # Handle preview image upload
        if preview_image := cleaned_input.get("preview_image"):
            cleaned_input["preview_image"] = info.context.FILES.get(preview_image)
            if cleaned_input["preview_image"]:
                cleaned_input["preview_image"] = clean_image_file(
                    cleaned_input, "preview_image", MarketplaceErrorCode
                )

        # Validate template_data is a dict if provided
        if template_data := cleaned_input.get("template_data"):
            if not isinstance(template_data, dict):
                raise ValidationError(
                    {
                        "template_data": ValidationError(
                            "template_data must be a valid JSON object.",
                            code=MarketplaceErrorCode.INVALID.value,
                        )
                    }
                )

        # Ensure only one default theme
        if cleaned_input.get("is_default", False):
            existing_default = models.Theme.objects.using(
                get_database_connection_name(info.context)
            ).filter(is_default=True).exclude(pk=instance.pk)
            if existing_default.exists():
                existing_default.update(is_default=False)

        return cleaned_input

