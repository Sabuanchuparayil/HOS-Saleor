from django.apps import AppConfig as DjangoAppConfig


class MarketplaceConfig(DjangoAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "saleor.marketplace"
    verbose_name = "Marketplace"

    def ready(self):
        from . import signals  # noqa: F401
