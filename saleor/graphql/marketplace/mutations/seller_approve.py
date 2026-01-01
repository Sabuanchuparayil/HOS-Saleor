"""GraphQL mutation for approving a seller."""

import graphene

from ....core.tracing import traced_atomic_transaction
from ....permission.enums import MarketplacePermissions
from ...core.mutations import ModelWithExtRefMutation
from ...core.types import MarketplaceError
from ..enums import SellerStatusEnum
from ..types import Seller
from ....marketplace import models


class SellerApprove(ModelWithExtRefMutation):
    """Approve a seller, changing their status to ACTIVE."""

    class Arguments:
        id = graphene.ID(required=False, description="ID of a seller to approve.")
        external_reference = graphene.String(
            required=False, description="External ID of a seller to approve."
        )

    class Meta:
        description = "Approve a seller, activating their account."
        model = models.Seller
        object_type = Seller
        permissions = (MarketplacePermissions.MANAGE_SELLERS,)
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"

    @classmethod
    def perform_mutation(  # type: ignore[override]
        cls, _root, info, /, *, external_reference=None, id=None
    ):
        instance = cls.get_instance(info, external_reference=external_reference, id=id)
        
        with traced_atomic_transaction():
            old_status = instance.status
            instance.status = models.SellerStatus.ACTIVE
            instance.save(update_fields=["status"])
            
            # Send approval email if status changed
            if old_status != models.SellerStatus.ACTIVE:
                try:
                    send_seller_approval_email(instance)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error sending approval email to seller {instance.store_name}: {e}")
        
        return cls.success_response(instance)


def send_seller_approval_email(seller: models.Seller):
    """Send approval email to seller when their account is approved."""
    from django.core.mail import send_mail
    from django.conf import settings
    from django.contrib.sites.models import Site
    
    if not seller.owner or not seller.owner.email:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Cannot send approval email: seller {seller.store_name} has no owner email")
        return
    
    site = Site.objects.get_current()
    subject = f"Your {site.name} Seller Account Has Been Approved!"
    
    message = f"""
Hello {seller.owner.get_full_name() or seller.store_name},

Great news! Your seller account "{seller.store_name}" has been approved and is now active.

You can now:
1. Start adding products to your store
2. Configure your shipping methods
3. Set up payment processing
4. Begin receiving orders

If you need any assistance, please don't hesitate to contact our support team.

Best regards,
{site.name} Team
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[seller.owner.email],
            fail_silently=False,
        )
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Sent approval email to seller {seller.store_name} ({seller.owner.email})")
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send approval email to seller {seller.store_name}: {e}")
        raise

