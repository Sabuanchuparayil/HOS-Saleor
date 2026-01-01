"""GraphQL mutation for creating a seller."""

from decimal import Decimal

import graphene
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from saleor.account.models import User
from ....channel.models import Channel
from ...core.context import get_database_connection_name
from saleor.marketplace.models import Seller, SellerStatus
from saleor.permission.enums import MarketplacePermissions
from ...core import ResolveInfo
from ...core.mutations import DeprecatedModelMutation
from ...core.types import MarketplaceError
from ...core.utils import from_global_id_or_error
from ...core.validators import validate_slug_and_generate_if_needed
from ..inputs import SellerCreateInput
from ..types import Seller


class SellerCreate(DeprecatedModelMutation):
    """Create a new seller."""

    class Arguments:
        input = SellerCreateInput(
            required=True, description="Fields required to create a seller."
        )

    class Meta:
        description = "Creates a new seller."
        model = Seller._meta.model
        object_type = Seller
        permissions = (MarketplacePermissions.MANAGE_SELLERS,)
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"
        support_meta_field = True
        support_private_meta_field = True

    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)

        # Validate and set owner
        owner_id = cleaned_input.pop("owner_id", None)
        if owner_id:
            _, owner_pk = from_global_id_or_error(owner_id, "User")
            try:
                owner = User.objects.using(
                    get_database_connection_name(info.context)
                ).get(pk=owner_pk)
                cleaned_input["owner"] = owner
            except User.DoesNotExist:
                raise ValidationError(
                    {"owner_id": ValidationError("User not found.", code="not_found")}
                )

        # Set channel if provided
        channel_id = cleaned_input.pop("channel_id", None)
        if channel_id:
            _, channel_pk = from_global_id_or_error(channel_id, "Channel")
            try:
                channel = Channel.objects.using(
                    get_database_connection_name(info.context)
                ).get(pk=channel_pk)
                cleaned_input["channel"] = channel
            except Channel.DoesNotExist:
                raise ValidationError(
                    {
                        "channel_id": ValidationError(
                            "Channel not found.", code="not_found"
                        )
                    }
                )

        # Set tax_origin_address if provided
        tax_origin_address_id = cleaned_input.pop("tax_origin_address_id", None)
        if tax_origin_address_id:
            from saleor.account.models import Address

            _, address_pk = from_global_id_or_error(tax_origin_address_id, "Address")
            try:
                address = Address.objects.using(
                    get_database_connection_name(info.context)
                ).get(pk=address_pk)
                cleaned_input["tax_origin_address"] = address
            except Address.DoesNotExist:
                raise ValidationError(
                    {
                        "tax_origin_address_id": ValidationError(
                            "Address not found.", code="not_found"
                        )
                    }
                )

        # Validate slug and generate if needed
        store_name = cleaned_input.get("store_name", "")
        if store_name:
            slug = cleaned_input.get("slug")
            if not slug:
                slug = slugify(store_name)
            cleaned_input["slug"] = validate_slug_and_generate_if_needed(
                instance, store_name, slug
            )

        # Set default status if not provided
        if "status" not in cleaned_input:
            cleaned_input["status"] = SellerStatus.PENDING

        # Set default platform_fee_percentage if not provided
        if "platform_fee_percentage" not in cleaned_input:
            cleaned_input["platform_fee_percentage"] = Decimal("10.00")

        return cleaned_input
