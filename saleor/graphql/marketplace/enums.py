"""GraphQL enums for marketplace."""

from typing import Final

import graphene

from saleor.marketplace.models import (
    DistributorCategory,
    FulfillmentMethod,
    ProductApprovalStatus,
    ReturnRequestStatus,
    SellerDomainStatus,
    SellerStatus,
    SellerType,
    SettlementStatus,
    TaxRegistrationType,
)
from saleor.marketplace.models import PricingType
from ..core.doc_category import DOC_CATEGORY_MARKETPLACE
from ..core.enums import to_enum

SellerStatusEnum: Final[graphene.Enum] = to_enum(
    SellerStatus, type_name="SellerStatusEnum"
)
SellerStatusEnum.doc_category = DOC_CATEGORY_MARKETPLACE

SellerDomainStatusEnum: Final[graphene.Enum] = to_enum(
    SellerDomainStatus, type_name="SellerDomainStatusEnum"
)
SellerDomainStatusEnum.doc_category = DOC_CATEGORY_MARKETPLACE

TaxRegistrationTypeEnum: Final[graphene.Enum] = to_enum(
    TaxRegistrationType, type_name="TaxRegistrationTypeEnum"
)
TaxRegistrationTypeEnum.doc_category = DOC_CATEGORY_MARKETPLACE

SettlementStatusEnum: Final[graphene.Enum] = to_enum(
    SettlementStatus, type_name="SettlementStatusEnum"
)
SettlementStatusEnum.doc_category = DOC_CATEGORY_MARKETPLACE

SellerTypeEnum: Final[graphene.Enum] = to_enum(
    SellerType, type_name="SellerTypeEnum"
)
SellerTypeEnum.doc_category = DOC_CATEGORY_MARKETPLACE

DistributorCategoryEnum: Final[graphene.Enum] = to_enum(
    DistributorCategory, type_name="DistributorCategoryEnum"
)
DistributorCategoryEnum.doc_category = DOC_CATEGORY_MARKETPLACE

ProductApprovalStatusEnum: Final[graphene.Enum] = to_enum(
    ProductApprovalStatus, type_name="ProductApprovalStatusEnum"
)
ProductApprovalStatusEnum.doc_category = DOC_CATEGORY_MARKETPLACE

FulfillmentMethodEnum: Final[graphene.Enum] = to_enum(
    FulfillmentMethod, type_name="FulfillmentMethodEnum"
)
FulfillmentMethodEnum.doc_category = DOC_CATEGORY_MARKETPLACE

ReturnRequestStatusEnum: Final[graphene.Enum] = to_enum(
    ReturnRequestStatus, type_name="ReturnRequestStatusEnum"
)
ReturnRequestStatusEnum.doc_category = DOC_CATEGORY_MARKETPLACE

PricingTypeEnum: Final[graphene.Enum] = to_enum(
    PricingType, type_name="PricingTypeEnum"
)
PricingTypeEnum.doc_category = DOC_CATEGORY_MARKETPLACE
