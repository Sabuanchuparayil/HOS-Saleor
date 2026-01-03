import os

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Configure and activate Saleor Stripe gateway plugin for all channels."

    def add_arguments(self, parser):
        parser.add_argument(
            "--public",
            dest="public_api_key",
            default=os.environ.get("STRIPE_PUBLIC_API_KEY"),
            help="Stripe publishable key (e.g. pk_test_...). Defaults to STRIPE_PUBLIC_API_KEY.",
        )
        parser.add_argument(
            "--secret",
            dest="secret_api_key",
            default=os.environ.get("STRIPE_SECRET_API_KEY"),
            help="Stripe secret key (e.g. sk_test_...). Defaults to STRIPE_SECRET_API_KEY.",
        )
        parser.add_argument(
            "--activate",
            action="store_true",
            default=True,
            help="Activate the plugin (default: true).",
        )
        parser.add_argument(
            "--auto-capture",
            dest="auto_capture",
            default=os.environ.get("STRIPE_AUTOMATIC_CAPTURE", "true"),
            help="Automatic capture (true/false). Defaults to STRIPE_AUTOMATIC_CAPTURE=true.",
        )
        parser.add_argument(
            "--supported-currencies",
            dest="supported_currencies",
            default=os.environ.get("STRIPE_SUPPORTED_CURRENCIES", ""),
            help="Comma-separated currency codes. Defaults to STRIPE_SUPPORTED_CURRENCIES.",
        )
        parser.add_argument(
            "--include-receipt-email",
            dest="include_receipt_email",
            default=os.environ.get("STRIPE_INCLUDE_RECEIPT_EMAIL", "true"),
            help="Include receipt email (true/false). Defaults to STRIPE_INCLUDE_RECEIPT_EMAIL=true.",
        )

    def handle(self, *args, **options):
        from saleor.channel.models import Channel
        from saleor.plugins.models import PluginConfiguration
        from saleor.payment.gateways.stripe.consts import PLUGIN_ID, PLUGIN_NAME
        from saleor.payment.gateways.stripe.plugin import StripeGatewayPlugin

        public_key = options["public_api_key"]
        secret_key = options["secret_api_key"]

        if not public_key or not secret_key:
            raise CommandError(
                "Stripe keys are required. Provide --public/--secret or set "
                "STRIPE_PUBLIC_API_KEY and STRIPE_SECRET_API_KEY."
            )

        auto_capture = str(options["auto_capture"]).strip().lower() in ("1", "true", "yes", "y")
        include_receipt_email = str(options["include_receipt_email"]).strip().lower() in (
            "1",
            "true",
            "yes",
            "y",
        )
        supported_currencies = (options["supported_currencies"] or "").strip()
        activate = bool(options["activate"])

        channels = Channel.objects.all()
        if not channels.exists():
            raise CommandError("No channels found. Create a channel first.")

        updated = 0
        for channel in channels:
            plugin_config, _ = PluginConfiguration.objects.get_or_create(
                identifier=PLUGIN_ID,
                channel=channel,
                defaults={
                    "name": PLUGIN_NAME,
                    "active": False,
                    "configuration": StripeGatewayPlugin.DEFAULT_CONFIGURATION,
                },
            )

            # Ensure base config exists
            configuration = plugin_config.configuration or []
            if not isinstance(configuration, list):
                configuration = []

            def upsert(name: str, value):
                for item in configuration:
                    if item.get("name") == name:
                        item["value"] = value
                        return
                configuration.append({"name": name, "value": value})

            upsert("public_api_key", public_key)
            upsert("secret_api_key", secret_key)
            upsert("automatic_payment_capture", auto_capture)
            upsert("supported_currencies", supported_currencies)
            upsert("include_receipt_email", include_receipt_email)

            plugin_config.name = plugin_config.name or PLUGIN_NAME
            plugin_config.configuration = configuration
            if activate:
                plugin_config.active = True
            plugin_config.save(update_fields=["name", "active", "configuration"])
            updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Stripe gateway configured for {updated} channel(s). "
                f"Plugin identifier: {PLUGIN_ID}"
            )
        )

