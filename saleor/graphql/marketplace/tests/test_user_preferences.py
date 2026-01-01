"""Tests for user preferences GraphQL API."""

import json

import pytest
from django.contrib.auth import get_user_model

from ...tests.utils import assert_no_permission, get_graphql_content

User = get_user_model()

USER_PREFERENCES_QUERY = """
    query UserPreferences {
        userPreferences {
            themeId
            languageCode
            currencyCode
            timezone
            emailNotifications
            marketingEmails
            recentlyViewedProductsLimit
        }
    }
"""

USER_PREFERENCES_UPDATE_MUTATION = """
    mutation UserPreferencesUpdate($input: UserPreferencesInput!) {
        userPreferencesUpdate(input: $input) {
            preferences {
                themeId
                languageCode
                currencyCode
                timezone
                emailNotifications
                marketingEmails
                recentlyViewedProductsLimit
            }
            marketplaceErrors {
                field
                message
                code
            }
        }
    }
"""


def test_user_preferences_query_unauthenticated(api_client):
    """Test that unauthenticated users cannot query preferences."""
    response = api_client.post_graphql(USER_PREFERENCES_QUERY)
    assert response.status_code == 200
    content = get_graphql_content(response)
    assert content["data"]["userPreferences"] is None


def test_user_preferences_query_authenticated(user_api_client):
    """Test querying user preferences for authenticated user."""
    response = user_api_client.post_graphql(USER_PREFERENCES_QUERY)
    assert response.status_code == 200
    content = get_graphql_content(response)
    assert content["data"]["userPreferences"] is not None
    preferences = content["data"]["userPreferences"]
    # Default values should be returned
    assert preferences["emailNotifications"] is True
    assert preferences["marketingEmails"] is False
    assert preferences["recentlyViewedProductsLimit"] == 10
    assert preferences["themeId"] is None
    assert preferences["languageCode"] is None
    assert preferences["currencyCode"] is None
    assert preferences["timezone"] is None


def test_user_preferences_update_basic_fields(user_api_client):
    """Test updating basic preference fields."""
    variables = {
        "input": {
            "languageCode": "en",
            "currencyCode": "USD",
            "timezone": "America/New_York",
            "emailNotifications": True,
            "marketingEmails": False,
            "recentlyViewedProductsLimit": 20,
        }
    }

    response = user_api_client.post_graphql(USER_PREFERENCES_UPDATE_MUTATION, variables)
    assert response.status_code == 200
    content = get_graphql_content(response)
    assert not content["data"]["userPreferencesUpdate"]["marketplaceErrors"]
    preferences = content["data"]["userPreferencesUpdate"]["preferences"]
    
    assert preferences["languageCode"] == "en"
    assert preferences["currencyCode"] == "USD"
    assert preferences["timezone"] == "America/New_York"
    assert preferences["emailNotifications"] is True
    assert preferences["marketingEmails"] is False
    assert preferences["recentlyViewedProductsLimit"] == 20

    # Verify preferences are stored in metadata (as snake_case keys)
    user = user_api_client.user
    user.refresh_from_db()
    preferences_metadata = user.metadata.get("preferences", {})
    assert preferences_metadata["language_code"] == "en"
    assert preferences_metadata["currency_code"] == "USD"
    assert preferences_metadata["timezone"] == "America/New_York"
    assert preferences_metadata["email_notifications"] is True
    assert preferences_metadata["marketing_emails"] is False
    assert preferences_metadata["recently_viewed_products_limit"] == 20


def test_user_preferences_update_with_theme(user_api_client, db):
    """Test updating preferences with a theme ID."""
    import graphene
    from saleor.marketplace.models import Theme

    # Create a test theme
    theme = Theme.objects.create(
        name="Test Theme",
        slug="test-theme",
        is_active=True,
        template_data={},
    )

    theme_global_id = graphene.Node.to_global_id("Theme", theme.id)
    variables = {
        "input": {
            "themeId": theme_global_id,
            "languageCode": "es",
        }
    }

    response = user_api_client.post_graphql(USER_PREFERENCES_UPDATE_MUTATION, variables)
    assert response.status_code == 200
    content = get_graphql_content(response)
    assert not content["data"]["userPreferencesUpdate"]["marketplaceErrors"]
    preferences = content["data"]["userPreferencesUpdate"]["preferences"]
    
    assert preferences["themeId"] == theme_global_id
    assert preferences["languageCode"] == "es"

    # Verify theme is stored in metadata (as GlobalID string)
    user = user_api_client.user
    user.refresh_from_db()
    preferences_metadata = user.metadata.get("preferences", {})
    assert preferences_metadata["theme_id"] == theme_global_id


def test_user_preferences_update_invalid_theme(user_api_client):
    """Test that invalid theme ID returns error."""
    import graphene
    import uuid

    # Create a fake GlobalID for a non-existent theme
    fake_theme_id = graphene.Node.to_global_id("Theme", uuid.uuid4())
    variables = {
        "input": {
            "themeId": fake_theme_id,
        }
    }

    response = user_api_client.post_graphql(USER_PREFERENCES_UPDATE_MUTATION, variables)
    assert response.status_code == 200
    content = get_graphql_content(response)
    errors = content["data"]["userPreferencesUpdate"]["marketplaceErrors"]
    assert len(errors) > 0
    assert errors[0]["field"] == "themeId"
    assert errors[0]["code"] == "NOT_FOUND"


def test_user_preferences_update_invalid_limit(user_api_client):
    """Test that invalid recently viewed products limit returns error."""
    variables = {
        "input": {
            "recentlyViewedProductsLimit": 150,  # Exceeds max limit of 100
        }
    }

    response = user_api_client.post_graphql(USER_PREFERENCES_UPDATE_MUTATION, variables)
    assert response.status_code == 200
    content = get_graphql_content(response)
    errors = content["data"]["userPreferencesUpdate"]["marketplaceErrors"]
    assert len(errors) > 0
    assert errors[0]["field"] == "recentlyViewedProductsLimit"
    assert errors[0]["code"] == "INVALID"


def test_user_preferences_update_partial_update(user_api_client):
    """Test that partial updates work correctly (only update provided fields)."""
    # First, set some preferences
    initial_variables = {
        "input": {
            "languageCode": "en",
            "currencyCode": "USD",
            "emailNotifications": True,
        }
    }
    user_api_client.post_graphql(USER_PREFERENCES_UPDATE_MUTATION, initial_variables)

    # Then, update only one field
    update_variables = {
        "input": {
            "languageCode": "es",
        }
    }

    response = user_api_client.post_graphql(USER_PREFERENCES_UPDATE_MUTATION, update_variables)
    assert response.status_code == 200
    content = get_graphql_content(response)
    preferences = content["data"]["userPreferencesUpdate"]["preferences"]
    
    # languageCode should be updated
    assert preferences["languageCode"] == "es"
    # currencyCode should remain from previous update
    assert preferences["currencyCode"] == "USD"
    # emailNotifications should remain from previous update
    assert preferences["emailNotifications"] is True


def test_user_preferences_update_unauthenticated(api_client):
    """Test that unauthenticated users cannot update preferences."""
    variables = {
        "input": {
            "languageCode": "en",
        }
    }

    response = api_client.post_graphql(USER_PREFERENCES_UPDATE_MUTATION, variables)
    assert response.status_code == 200
    content = get_graphql_content(response)
    assert content["data"]["userPreferencesUpdate"] is None
    assert len(content["errors"]) > 0


def test_user_preferences_update_remove_theme(user_api_client, db):
    """Test removing theme preference by setting it to null."""
    import graphene
    from saleor.marketplace.models import Theme

    # First, set a theme
    theme = Theme.objects.create(
        name="Test Theme",
        slug="test-theme",
        is_active=True,
        template_data={},
    )

    theme_global_id = graphene.Node.to_global_id("Theme", theme.id)
    initial_variables = {
        "input": {
            "themeId": theme_global_id,
        }
    }
    user_api_client.post_graphql(USER_PREFERENCES_UPDATE_MUTATION, initial_variables)

    # Then, remove the theme by setting it to null
    remove_variables = {
        "input": {
            "themeId": None,
        }
    }

    response = user_api_client.post_graphql(USER_PREFERENCES_UPDATE_MUTATION, remove_variables)
    assert response.status_code == 200
    content = get_graphql_content(response)
    preferences = content["data"]["userPreferencesUpdate"]["preferences"]
    
    assert preferences["themeId"] is None

    # Verify theme is removed from metadata
    user = user_api_client.user
    user.refresh_from_db()
    preferences_metadata = user.metadata.get("preferences", {})
    assert "theme_id" not in preferences_metadata

