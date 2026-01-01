"""GraphQL mutation for newsletter subscription."""

import graphene
from django.core.exceptions import ValidationError
from django.utils import timezone

from ....core.tracing import traced_atomic_transaction
from ...core.context import get_database_connection_name
from saleor.marketplace import models
from saleor.marketplace.error_codes import MarketplaceErrorCode
from ...core import ResolveInfo
from ...core.mutations import BaseMutation
from ...core.types import MarketplaceError
from ..inputs import NewsletterSubscribeInput
from ..types import NewsletterSubscription


class NewsletterSubscribe(BaseMutation):
    """Subscribe to newsletter."""

    subscription = graphene.Field(
        NewsletterSubscription, description="Newsletter subscription instance."
    )

    class Arguments:
        input = NewsletterSubscribeInput(
            required=True, description="Fields required to subscribe to newsletter."
        )

    class Meta:
        description = "Subscribe an email address to the newsletter."
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(  # type: ignore[override]
        cls, _root, info: ResolveInfo, /, *, input
    ):
        email = input.get("email", "").strip().lower()
        source = input.get("source", "")

        if not email:
            raise ValidationError(
                {
                    "email": ValidationError(
                        "Email is required.",
                        code=MarketplaceErrorCode.REQUIRED.value,
                    )
                }
            )

        # Check if user is authenticated
        user = getattr(info.context, "user", None)
        if user and hasattr(user, "email") and user.email.lower() == email:
            user_id = user.id
        else:
            user_id = None

        connection_name = get_database_connection_name(info.context)

        with traced_atomic_transaction():
            # Check for existing subscription
            existing = models.NewsletterSubscription.objects.using(
                connection_name
            ).filter(email=email).first()

            if existing:
                # Reactivate if previously unsubscribed
                if not existing.is_active:
                    existing.is_active = True
                    existing.unsubscribed_at = None
                    existing.source = source or existing.source
                    if user_id and not existing.user_id:
                        existing.user_id = user_id
                    existing.save()
                    subscription = existing
                else:
                    # Already subscribed
                    subscription = existing
            else:
                # Create new subscription
                subscription = models.NewsletterSubscription.objects.using(
                    connection_name
                ).create(
                    email=email,
                    source=source,
                    user_id=user_id,
                    is_active=True,
                    # confirmed_at will be set when double opt-in is completed
                )

        return cls(subscription=subscription)


class NewsletterUnsubscribe(BaseMutation):
    """Unsubscribe from newsletter."""

    subscription = graphene.Field(
        NewsletterSubscription, description="Newsletter subscription instance."
    )

    class Arguments:
        email = graphene.String(
            required=True, description="Email address to unsubscribe."
        )

    class Meta:
        description = "Unsubscribe an email address from the newsletter."
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(  # type: ignore[override]
        cls, _root, info: ResolveInfo, /, *, email
    ):
        email = email.strip().lower()

        if not email:
            raise ValidationError(
                {
                    "email": ValidationError(
                        "Email is required.",
                        code=MarketplaceErrorCode.REQUIRED.value,
                    )
                }
            )

        connection_name = get_database_connection_name(info.context)

        with traced_atomic_transaction():
            subscription = models.NewsletterSubscription.objects.using(
                connection_name
            ).filter(email=email).first()

            if subscription:
                subscription.is_active = False
                subscription.unsubscribed_at = timezone.now()
                subscription.save()
            else:
                # Create inactive subscription record for tracking
                subscription = models.NewsletterSubscription.objects.using(
                    connection_name
                ).create(
                    email=email,
                    is_active=False,
                    unsubscribed_at=timezone.now(),
                )

        return cls(subscription=subscription)

