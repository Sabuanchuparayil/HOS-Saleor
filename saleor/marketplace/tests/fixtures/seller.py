"""Pytest fixtures for seller models."""

import pytest

from ...models import Seller, SellerStatus


@pytest.fixture
def seller(db, channel, customer_user):
    """Create a test seller."""
    from ...models import Seller

    return Seller.objects.create(
        store_name="Test Seller",
        slug="test-seller",
        description="A test seller",
        owner=customer_user,
        channel=channel,
        status=SellerStatus.ACTIVE,
        platform_fee_percentage=10.00,
    )


@pytest.fixture
def active_seller(seller):
    """Create an active seller."""
    seller.status = SellerStatus.ACTIVE
    seller.save()
    return seller


@pytest.fixture
def pending_seller(seller):
    """Create a pending seller."""
    seller.status = SellerStatus.PENDING
    seller.save()
    return seller


@pytest.fixture
def seller_with_domain(seller, db):
    """Create a seller with a domain."""
    from ...models import SellerDomain, SellerDomainStatus

    domain = SellerDomain.objects.create(
        seller=seller,
        domain="test-store.example.com",
        is_primary=True,
        status=SellerDomainStatus.ACTIVE,
    )
    return seller
