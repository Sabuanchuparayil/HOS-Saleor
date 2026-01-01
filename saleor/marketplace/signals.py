"""Signal handlers for marketplace functionality."""

import logging

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver

from .models import (
    FulfillmentCenter,
    InventorySync,
    OrderRoutingRule,
    ProductSubmission,
    ReturnRequest,
    Seller,
    SellerDomain,
    SellerLogisticsConfig,
    SellerStorefrontSettings,
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Seller)
def create_seller_defaults(sender, instance: Seller, created: bool, **kwargs):
    """Create default settings and configurations when a seller is created."""
    if created:
        # Create default storefront settings
        SellerStorefrontSettings.objects.get_or_create(
            seller=instance,
            defaults={
                "primary_color": "#000000",
                "secondary_color": "#FFFFFF",
            },
        )
        logger.info(f"Created default storefront settings for seller {instance.store_name}")

        # Create default logistics configuration
        SellerLogisticsConfig.objects.get_or_create(
            seller=instance,
            defaults={
                "fulfillment_method": "marketplace_fulfill",
                "handling_time_days": 3 if instance.seller_type == "b2c_retail" else 7,
            },
        )
        logger.info(f"Created default logistics config for seller {instance.store_name}")

        # Create default discount configuration
        from .models_discount import SellerDiscountConfig
        SellerDiscountConfig.objects.get_or_create(
            seller=instance,
            defaults={
                "allow_sku_level_discounts": True,
                "allow_category_level_discounts": True,
                "allow_seller_level_discounts": True,
            },
        )
        logger.info(f"Created default discount config for seller {instance.store_name}")
        
        # Send welcome email to seller
        try:
            send_seller_welcome_email(instance)
        except Exception as e:
            logger.error(f"Error sending welcome email to seller {instance.store_name}: {e}")


def send_seller_welcome_email(seller: Seller):
    """Send welcome email to newly registered seller."""
    from django.core.mail import send_mail
    from django.conf import settings
    from django.contrib.sites.models import Site
    
    if not seller.owner or not seller.owner.email:
        logger.warning(f"Cannot send welcome email: seller {seller.store_name} has no owner email")
        return
    
    site = Site.objects.get_current()
    subject = f"Welcome to {site.name} Marketplace!"
    
    message = f"""
Hello {seller.owner.get_full_name() or seller.store_name},

Welcome to {site.name}! Your seller account "{seller.store_name}" has been created successfully.

Your account status: {seller.get_status_display()}

Next steps:
1. Complete your seller profile
2. Add your products
3. Configure your shipping and payment settings

If you have any questions, please contact our support team.

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
        logger.info(f"Sent welcome email to seller {seller.store_name} ({seller.owner.email})")
    except Exception as e:
        logger.error(f"Failed to send welcome email to seller {seller.store_name}: {e}")
        raise


@receiver(pre_save, sender=Seller)
def handle_seller_type_change(sender, instance: Seller, **kwargs):
    """Handle seller type changes and update related configurations."""
    if instance.pk:
        try:
            old_instance = Seller.objects.get(pk=instance.pk)
            if old_instance.seller_type != instance.seller_type:
                # Seller type changed, update logistics config
                try:
                    logistics_config = instance.logistics_config
                    # Update handling time based on new seller type
                    if instance.seller_type == "b2c_retail":
                        logistics_config.handling_time_days = 3
                    elif instance.seller_type == "b2b_wholesale":
                        logistics_config.handling_time_days = 7
                    logistics_config.save()
                    logger.info(
                        f"Updated logistics config for seller {instance.store_name} due to type change"
                    )
                except SellerLogisticsConfig.DoesNotExist:
                    pass
        except Seller.DoesNotExist:
            pass


@receiver(post_save, sender=SellerDomain)
def handle_domain_verification(sender, instance: SellerDomain, created: bool, **kwargs):
    """Handle domain verification and trigger SSL setup."""
    if instance.status == "verified" and instance.verified_at:
        # Domain verified, trigger SSL certificate setup
        # This would integrate with SSL certificate management service
        logger.info(f"Domain {instance.domain} verified for seller {instance.seller.store_name}")
        # TODO: Integrate with SSL certificate management (Let's Encrypt, etc.)


@receiver(post_save, sender="product.Product")
def handle_product_assignment(sender, instance, created: bool, **kwargs):
    """Handle product assignment to seller and validate seller status."""
    from .models import ProductSubmission

    seller = getattr(instance, "seller", None)
    if seller:
        # Validate seller is active
        if not seller.is_active:
            logger.warning(
                f"Product {instance.name} assigned to inactive seller {seller.store_name}"
            )

        # If product is seller-created and pending approval, create submission record
        if created and instance.approval_status == "pending":
            ProductSubmission.objects.get_or_create(
                seller=seller,
                product=instance,
                defaults={"status": "pending"},
            )
            logger.info(
                f"Created product submission for {instance.name} by seller {seller.store_name}"
            )

        # Enforce SKU exclusivity
        if instance.is_exclusive_to_seller:
            from ..product.models import ProductVariant

            for variant in instance.variants.all():
                if variant.sku:
                    # Check for other products with same SKU assigned to different seller
                    conflicting_products = sender.objects.filter(
                        variants__sku=variant.sku,
                        seller__isnull=False,
                    ).exclude(pk=instance.pk)

                    if conflicting_products.exists():
                        logger.warning(
                            f"SKU {variant.sku} conflict detected for product {instance.name}"
                        )


@receiver(post_save, sender=ProductSubmission)
def handle_product_submission(sender, instance: ProductSubmission, created: bool, **kwargs):
    """Handle product submission and notify admin."""
    if created:
        logger.info(
            f"Product {instance.product.name} submitted by seller {instance.seller.store_name} for approval"
        )
        # TODO: Send notification to admin for approval


@receiver(post_save, sender=ProductSubmission)
def handle_product_approval(sender, instance: ProductSubmission, **kwargs):
    """Handle product approval/rejection and update product status."""
    if instance.status in ["approved", "rejected", "requires_revision"]:
        # Update product approval status
        instance.product.approval_status = instance.status
        instance.product.save(update_fields=["approval_status"])

        if instance.status == "approved":
            logger.info(f"Product {instance.product.name} approved")
            # TODO: Notify seller of approval
        elif instance.status == "rejected":
            logger.info(f"Product {instance.product.name} rejected")
            # TODO: Notify seller of rejection with admin notes


@receiver(post_save, sender="order.OrderLine")
def handle_order_line_denormalization(sender, instance, created: bool, **kwargs):
    """Ensure seller information is properly denormalized in order lines."""
    if created:
        # Seller information should already be denormalized in complete_checkout.py
        # This signal is a safety check
        if not instance.seller and hasattr(instance, "variant"):
            product = getattr(instance.variant, "product", None)
            if product:
                seller = getattr(product, "seller", None)
                if seller:
                    instance.seller = seller
                    instance.seller_name = seller.store_name
                    instance.save(update_fields=["seller", "seller_name"])
                    logger.debug(
                        f"Denormalized seller info for order line {instance.id}"
                    )


@receiver(post_save, sender="warehouse.Stock")
def handle_inventory_change(sender, instance, **kwargs):
    """Trigger real-time inventory sync when stock changes."""
    from .services.inventory_sync import sync_inventory_for_variant

    variant = instance.product_variant
    if variant:
        # Sync inventory for this variant
        try:
            sync_inventory_for_variant(
                variant,
                warehouse=instance.warehouse,
                sync_method="webhook",
            )
            logger.debug(f"Synced inventory for variant {variant.sku}")
        except Exception as e:
            logger.error(f"Error syncing inventory for variant {variant.sku}: {e}")


@receiver(post_save, sender="order.Order")
def handle_order_creation(sender, instance, created: bool, **kwargs):
    """Apply automatic routing to nearest fulfillment center when order is created."""
    if created and instance.shipping_address:
        from .shipping import route_order_to_fulfillment_center

        # Route order to fulfillment center
        fulfillment_center = route_order_to_fulfillment_center(instance)
        if fulfillment_center:
            # Store fulfillment center in order metadata
            instance.store_value_in_metadata(
                {"fulfillment_center_id": str(fulfillment_center.id)}
            )
            logger.info(
                f"Order {instance.number} routed to fulfillment center {fulfillment_center.name}"
            )
