"""GraphQL mutation for updating user preferences."""

import json
from typing import TYPE_CHECKING

import graphene
from django.core.exceptions import ValidationError

from ....account import models as account_models
from ....core.tracing import traced_atomic_transaction
from ...core.context import get_database_connection_name
from ...core import ResolveInfo
from ...core.mutations import BaseMutation
from ...core.types import MarketplaceError
from ...core.utils import from_global_id_or_error
from ..inputs import UserPreferencesInput
from ..types import UserPreferences
from saleor.marketplace import error_codes

if TYPE_CHECKING:
    from ....account.models import User


PREFERENCES_METADATA_KEY = "preferences"


class UserPreferencesUpdate(BaseMutation):
    """Update user preferences stored in metadata."""

    preferences = graphene.Field(
        UserPreferences, description="Updated user preferences."
    )

    class Arguments:
        input = UserPreferencesInput(
            required=True, description="User preferences to update."
        )

    class Meta:
        description = "Updates user preferences stored in user metadata."
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        """Perform the mutation."""
        user = info.context.user
        if not user or not user.is_authenticated:
            raise ValidationError(
                {
                    "user": ValidationError(
                        "You must be authenticated to update preferences.",
                        code=error_codes.MarketplaceErrorCode.INVALID.value,
                    )
                }
            )

        input_data = data.get("input", {})

        # Get current preferences from metadata
        preferences_metadata = user.metadata.get(PREFERENCES_METADATA_KEY, {})
        if isinstance(preferences_metadata, str):
            try:
                preferences_metadata = json.loads(preferences_metadata)
            except (json.JSONDecodeError, TypeError):
                preferences_metadata = {}

        # Update preferences with new values
        updated_preferences = preferences_metadata.copy()

        # Map GraphQL camelCase input fields to snake_case metadata keys
        field_mapping = {
            "themeId": "theme_id",
            "languageCode": "language_code",
            "currencyCode": "currency_code",
            "timezone": "timezone",
            "emailNotifications": "email_notifications",
            "marketingEmails": "marketing_emails",
            "recentlyViewedProductsLimit": "recently_viewed_products_limit",
        }

        # Handle theme_id if provided
        if "themeId" in input_data and input_data["themeId"] is not None:
            theme_id = input_data["themeId"]
            # Validate theme exists
            from saleor.marketplace import models

            _, theme_pk = from_global_id_or_error(theme_id, "Theme")
            try:
                theme = models.Theme.objects.using(
                    get_database_connection_name(info.context)
                ).get(pk=theme_pk, is_active=True)
                # Store theme ID as GlobalID string for consistency
                updated_preferences["theme_id"] = graphene.Node.to_global_id("Theme", theme.id)
            except models.Theme.DoesNotExist:
                raise ValidationError(
                    {
                        "themeId": ValidationError(
                            "Theme not found or inactive.",
                            code=error_codes.MarketplaceErrorCode.NOT_FOUND.value,
                        )
                    }
                )
        elif "themeId" in input_data and input_data["themeId"] is None:
            # Remove theme_id preference
            updated_preferences.pop("theme_id", None)

        # Update other preference fields
        for graphql_field, metadata_key in field_mapping.items():
            if graphql_field == "themeId":
                continue  # Already handled above
            if graphql_field in input_data:
                value = input_data[graphql_field]
                if value is not None:
                    updated_preferences[metadata_key] = value
                else:
                    updated_preferences.pop(metadata_key, None)

        # Validate recently_viewed_products_limit if provided
        if "recently_viewed_products_limit" in updated_preferences:
            limit = updated_preferences["recently_viewed_products_limit"]
            if not isinstance(limit, int) or limit < 0 or limit > 100:
                raise ValidationError(
                    {
                        "recentlyViewedProductsLimit": ValidationError(
                            "Limit must be between 0 and 100.",
                            code=error_codes.MarketplaceErrorCode.INVALID.value,
                        )
                    }
                )

        # Save preferences to metadata
        with traced_atomic_transaction():
            user.store_value_in_metadata({PREFERENCES_METADATA_KEY: updated_preferences})
            user.save(update_fields=["metadata", "updated_at"])

        # Return updated preferences
        preferences = cls._build_preferences_object(updated_preferences, user)

        return cls(preferences=preferences)

    @classmethod
    def _build_preferences_object(cls, preferences_dict: dict, user: "User") -> UserPreferences:
        """Build UserPreferences object from metadata dictionary."""
        return UserPreferences(
            theme_id=preferences_dict.get("theme_id"),
            language_code=preferences_dict.get("language_code"),
            currency_code=preferences_dict.get("currency_code"),
            timezone=preferences_dict.get("timezone"),
            email_notifications=preferences_dict.get("email_notifications", True),
            marketing_emails=preferences_dict.get("marketing_emails", False),
            recently_viewed_products_limit=preferences_dict.get(
                "recently_viewed_products_limit", 10
            ),
        )

