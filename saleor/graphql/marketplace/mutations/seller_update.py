"""GraphQL mutation for updating a seller."""

import graphene
from django.core.exceptions import ValidationError

from ....account.models import Address, User
from ....channel.models import Channel
from ...core.context import get_database_connection_name
from saleor.marketplace import models
from ....permission.enums import MarketplacePermissions
from ...core import ResolveInfo
from ...core.mutations import ModelWithExtRefMutation
from ...core.types import MarketplaceError
from ...core.utils import from_global_id_or_error
from ...core.validators import validate_slug_and_generate_if_needed
from ..inputs import SellerUpdateInput
from ..types import Seller


class SellerUpdate(ModelWithExtRefMutation):
    """Update an existing seller."""

    class Arguments:
        id = graphene.ID(required=False, description="ID of a seller to update.")
        external_reference = graphene.String(
            required=False,
            description="External ID of a seller to update.",
        )
        input = SellerUpdateInput(
            required=True, description="Fields required to update a seller."
        )

    class Meta:
        description = "Updates an existing seller."
        model = models.Seller
        object_type = Seller
        permissions = (MarketplacePermissions.MANAGE_SELLERS,)
        error_type_class = MarketplaceError
        error_type_field = "marketplace_errors"
        support_meta_field = True
        support_private_meta_field = True

    @classmethod
    def clean_input(cls, info: ResolveInfo, instance, data, **kwargs):
        cleaned_input = super().clean_input(info, instance, data, **kwargs)

        # Update owner if provided
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

        # Update channel if provided
        channel_id = cleaned_input.pop("channel_id", None)
        if channel_id is not None:
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
            else:
                cleaned_input["channel"] = None

        # Update tax_origin_address if provided
        tax_origin_address_id = cleaned_input.pop("tax_origin_address_id", None)
        if tax_origin_address_id is not None:
            if tax_origin_address_id:
                _, address_pk = from_global_id_or_error(
                    tax_origin_address_id, "Address"
                )
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
            else:
                cleaned_input["tax_origin_address"] = None

        # Validate slug if store_name or slug is being updated
        store_name = cleaned_input.get("store_name")
        slug = cleaned_input.get("slug")
        if store_name or slug:
            current_store_name = instance.store_name if instance else ""
            current_slug = instance.slug if instance else ""
            store_name = store_name or current_store_name
            slug = slug or current_slug
            cleaned_input["slug"] = validate_slug_and_generate_if_needed(
                instance, store_name, slug
            )

        return cleaned_input
