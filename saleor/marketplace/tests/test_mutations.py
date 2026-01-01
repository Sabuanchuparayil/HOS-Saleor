"""Tests for marketplace GraphQL mutations."""

import pytest
from django.contrib.auth import get_user_model

from ...account.models import User
from ...channel.models import Channel
from ...graphql.tests.utils import get_graphql_content
from ..models import Seller, SellerStatus

User = get_user_model()


@pytest.fixture
def staff_user(db, staff_user):
    """Staff user with marketplace permissions."""
    from ...permission.enums import MarketplacePermissions
    
    staff_user.user_permissions.add(
        *[
            perm
            for perm in MarketplacePermissions
            if perm.value == MarketplacePermissions.MANAGE_SELLERS.value
        ]
    )
    return staff_user


@pytest.fixture
def staff_user_finance(db, staff_user):
    """Staff user with marketplace finance permissions."""
    from ...permission.enums import MarketplacePermissions
    
    staff_user.user_permissions.add(
        *[
            perm
            for perm in MarketplacePermissions
            if perm.value == MarketplacePermissions.MANAGE_FINANCE.value
        ]
    )
    return staff_user


SELLER_CREATE_MUTATION = """
    mutation SellerCreate($input: SellerCreateInput!) {
        sellerCreate(input: $input) {
            seller {
                id
                storeName
                slug
                status
                platformFeePercentage
            }
            marketplaceErrors {
                field
                code
                message
            }
        }
    }
"""


def test_seller_create_mutation(staff_api_client, channel, customer_user):
    """Test creating a seller via GraphQL."""
    # given
    variables = {
        "input": {
            "storeName": "Test Store",
            "slug": "test-store",
            "description": "A test store",
            "ownerId": str(customer_user.id),
            "channelId": str(channel.id),
            "platformFeePercentage": "15.00",
        }
    }

    # when
    response = staff_api_client.post_graphql(SELLER_CREATE_MUTATION, variables)

    # then
    content = get_graphql_content(response)
    assert not content["data"]["sellerCreate"]["marketplaceErrors"]
    seller_data = content["data"]["sellerCreate"]["seller"]
    assert seller_data["storeName"] == "Test Store"
    assert seller_data["slug"] == "test-store"
    assert seller_data["status"] == SellerStatus.PENDING.upper()


SELLER_UPDATE_MUTATION = """
    mutation SellerUpdate($id: ID!, $input: SellerUpdateInput!) {
        sellerUpdate(id: $id, input: $input) {
            seller {
                id
                storeName
                description
            }
            marketplaceErrors {
                field
                code
                message
            }
        }
    }
"""


def test_seller_update_mutation(staff_api_client, seller):
    """Test updating a seller via GraphQL."""
    # given
    seller_id = str(seller.id)
    variables = {
        "id": seller_id,
        "input": {
            "description": "Updated description",
        },
    }

    # when
    response = staff_api_client.post_graphql(SELLER_UPDATE_MUTATION, variables)

    # then
    content = get_graphql_content(response)
    assert not content["data"]["sellerUpdate"]["marketplaceErrors"]
    seller_data = content["data"]["sellerUpdate"]["seller"]
    assert seller_data["description"] == "Updated description"


SELLER_DELETE_MUTATION = """
    mutation SellerDelete($id: ID!) {
        sellerDelete(id: $id) {
            seller {
                id
            }
            marketplaceErrors {
                field
                code
                message
            }
        }
    }
"""


def test_seller_delete_mutation(staff_api_client, seller):
    """Test deleting a seller via GraphQL."""
    # given
    seller_id = str(seller.id)
    variables = {"id": seller_id}

    # when
    response = staff_api_client.post_graphql(SELLER_DELETE_MUTATION, variables)

    # then
    content = get_graphql_content(response)
    assert not content["data"]["sellerDelete"]["marketplaceErrors"]
    
    # Verify seller is deleted
    assert not Seller.objects.filter(id=seller.id).exists()


PRICING_RULE_CREATE_MUTATION = """
    mutation PricingRuleCreate(
        $productId: ID
        $sellerId: ID
        $pricingType: PricingTypeEnum!
        $discountPercentage: Decimal
        $fixedPrice: Decimal
        $isActive: Boolean
    ) {
        pricingRuleCreate(
            productId: $productId
            sellerId: $sellerId
            pricingType: $pricingType
            discountPercentage: $discountPercentage
            fixedPrice: $fixedPrice
            isActive: $isActive
        ) {
            pricingRule {
                id
                pricingType
                discountPercentage
                fixedPrice
                isActive
            }
            marketplaceErrors {
                field
                code
                message
            }
        }
    }
"""


def test_pricing_rule_create_with_product(staff_api_client, staff_user_finance, product):
    """Test creating a pricing rule for a product."""
    from ....graphql.core.utils import to_global_id_or_none
    
    # given
    product_id = to_global_id_or_none(product)
    variables = {
        "productId": product_id,
        "pricingType": "PROMOTIONAL",
        "discountPercentage": "10.00",
        "isActive": True,
    }

    # when
    response = staff_api_client.post_graphql(PRICING_RULE_CREATE_MUTATION, variables)

    # then
    content = get_graphql_content(response)
    assert not content["data"]["pricingRuleCreate"]["marketplaceErrors"]
    pricing_rule_data = content["data"]["pricingRuleCreate"]["pricingRule"]
    assert pricing_rule_data["pricingType"] == "PROMOTIONAL"
    assert pricing_rule_data["discountPercentage"] == "10.00"
    assert pricing_rule_data["isActive"] is True


def test_pricing_rule_create_with_seller(staff_api_client, staff_user_finance, seller):
    """Test creating a pricing rule for a seller."""
    from ....graphql.core.utils import to_global_id_or_none
    
    # given
    seller_id = to_global_id_or_none(seller)
    variables = {
        "sellerId": seller_id,
        "pricingType": "SEASONAL",
        "fixedPrice": "99.99",
        "isActive": True,
    }

    # when
    response = staff_api_client.post_graphql(PRICING_RULE_CREATE_MUTATION, variables)

    # then
    content = get_graphql_content(response)
    assert not content["data"]["pricingRuleCreate"]["marketplaceErrors"]
    pricing_rule_data = content["data"]["pricingRuleCreate"]["pricingRule"]
    assert pricing_rule_data["pricingType"] == "SEASONAL"
    assert pricing_rule_data["fixedPrice"] == "99.99"
    assert pricing_rule_data["isActive"] is True


def test_pricing_rule_create_validation_error(staff_api_client, staff_user_finance):
    """Test that creating a pricing rule without product_id or seller_id fails."""
    # given
    variables = {
        "pricingType": "PROMOTIONAL",
        "discountPercentage": "10.00",
    }

    # when
    response = staff_api_client.post_graphql(PRICING_RULE_CREATE_MUTATION, variables)

    # then
    content = get_graphql_content(response)
    errors = content["data"]["pricingRuleCreate"]["marketplaceErrors"]
    assert len(errors) > 0
    assert any("product_id" in error.get("field", "").lower() or "seller_id" in error.get("field", "").lower() for error in errors)



