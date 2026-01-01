"""GraphQL mutation for updating seller storefront settings."""

import graphene
from django.core.exceptions import ValidationError

from ...core.context import get_database_connection_name
from ....marketplace import error_codes, models
from ....permission.enums import MarketplacePermissions
from ...core import ResolveInfo
from ...core.mutations import BaseMutation
from ...core.types import MarketplaceError
from ...core.utils import from_global_id_or_error
from ..inputs import SellerStorefrontSettingsInput
from ..types import Seller, SellerStorefrontSettings, Theme


class SellerStorefrontSettingsUpdate(BaseMutation):
    """Update storefront settings for a seller."""

    class Arguments:
        seller_id = graphene.ID(
            required=True, description="ID of the seller to update settings for."
        )
        input = SellerStorefrontSettingsInput(
            required=True, description="Storefront settings to update."
        )

    seller = graphene.Field(Seller, description="The seller with updated settings.")
    settings = graphene.Field(
        SellerStorefrontSettings, description="The updated storefront settings."
    )

    class Meta:
        description = "Updates storefront settings for a seller."
        permissions = (MarketplacePermissions.MANAGE_SELLERS,)
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        """Perform the mutation."""
        seller_id = data.get("seller_id")
        input_data = data.get("input", {})

        # Get seller
        _, seller_pk = from_global_id_or_error(seller_id, Seller)
        try:
            seller = models.Seller.objects.using(
                get_database_connection_name(info.context)
            ).get(pk=seller_pk)
        except models.Seller.DoesNotExist:
            raise ValidationError(
                {
                    "seller_id": ValidationError(
                        "Seller not found.", code=error_codes.MarketplaceErrorCode.NOT_FOUND
                    )
                }
            )

        # Get or create storefront settings
        settings, created = models.SellerStorefrontSettings.objects.get_or_create(
            seller=seller
        )

        # Handle theme_id if provided
        if "theme_id" in input_data:
            theme_id = input_data.pop("theme_id")
            if theme_id:
                _, theme_pk = from_global_id_or_error(theme_id, Theme)
                try:
                    theme = models.Theme.objects.using(
                        get_database_connection_name(info.context)
                    ).get(pk=theme_pk)
                    settings.theme = theme
                except models.Theme.DoesNotExist:
                    raise ValidationError(
                        {
                            "theme_id": ValidationError(
                                "Theme not found.",
                                code=error_codes.MarketplaceErrorCode.NOT_FOUND,
                            )
                        }
                    )
            else:
                settings.theme = None

        # Update fields
        fields_to_update = [
            "primary_color",
            "secondary_color",
            "favicon",
            "storefront_logo",
            "custom_css",
            "meta_title",
            "meta_description",
            "facebook_url",
            "twitter_url",
            "instagram_url",
            "contact_email",
            "contact_phone",
            "theme_customizations",
        ]

        for field in fields_to_update:
            if field in input_data:
                value = input_data[field]
                # Validate theme_customizations is a dict if provided
                if field == "theme_customizations" and value is not None:
                    if not isinstance(value, dict):
                        raise ValidationError(
                            {
                                "theme_customizations": ValidationError(
                                    "theme_customizations must be a valid JSON object.",
                                    code=error_codes.MarketplaceErrorCode.INVALID,
                                )
                            }
                        )
                setattr(settings, field, value)

        settings.save()

        return cls(seller=seller, settings=settings)

