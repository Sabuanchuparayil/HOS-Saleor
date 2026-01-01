"""GraphQL mutation for creating a theme."""

import graphene
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from ....core.tracing import traced_atomic_transaction
from ...core.context import get_database_connection_name
from saleor.marketplace import models
from saleor.marketplace.error_codes import MarketplaceErrorCode
from ....permission.enums import MarketplacePermissions
from ...core import ResolveInfo
from ...core.mutations import DeprecatedModelMutation
from ...core.types import MarketplaceError
from ...core.validators import validate_slug_and_generate_if_needed
from ...core.validators.file import clean_image_file
from ..inputs import ThemeCreateInput
from ..types import Theme


class ThemeCreate(DeprecatedModelMutation):
    """Create a new theme."""

    class Arguments:
        input = ThemeCreateInput(
            required=True, description="Fields required to create a theme."
        )

    class Meta:
        description = "Creates a new theme template."
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

        # Validate slug and generate if needed
        name = cleaned_input.get("name", "")
        if name:
            slug = cleaned_input.get("slug")
            if not slug:
                slug = slugify(name)
            cleaned_input["slug"] = validate_slug_and_generate_if_needed(
                instance, name, slug
            )

        # Validate unique slug
        if "slug" in cleaned_input:
            existing = models.Theme.objects.using(
                get_database_connection_name(info.context)
            ).filter(slug=cleaned_input["slug"])
            if instance.pk:
                existing = existing.exclude(pk=instance.pk)
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
            ).filter(is_default=True)
            if instance.pk:
                existing_default = existing_default.exclude(pk=instance.pk)
            if existing_default.exists():
                # Set other default themes to False
                existing_default.update(is_default=False)

        return cleaned_input

