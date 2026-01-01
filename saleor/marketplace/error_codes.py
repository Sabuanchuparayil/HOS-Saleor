"""Error codes for marketplace app."""

from enum import Enum


class MarketplaceErrorCode(str, Enum):
    """Error codes for marketplace operations."""

    INVALID = "invalid"
    NOT_FOUND = "not_found"
    REQUIRED = "required"
    UNIQUE = "unique"
    INVALID_DOMAIN = "invalid_domain"
    DOMAIN_VERIFICATION_FAILED = "domain_verification_failed"
    PERMISSION_DENIED = "permission_denied"
    INVALID_SELLER = "invalid_seller"
    INVALID_PRODUCT = "invalid_product"
    INVALID_ORDER = "invalid_order"
    SELLER_NOT_ACTIVE = "seller_not_active"
    PRODUCT_NOT_APPROVED = "product_not_approved"
    INVALID_TAX_REGISTRATION = "invalid_tax_registration"
    INVALID_FULFILLMENT_CENTER = "invalid_fulfillment_center"
    INVALID_RETURN_REQUEST = "invalid_return_request"
    INVALID_PRICING_RULE = "invalid_pricing_rule"
    DOMAIN_ALREADY_IN_USE = "domain_already_in_use"
