import { gql } from "@apollo/client";

// Cart Mutations
export const ADD_TO_CART = gql`
  mutation AddToCart($checkoutId: ID!, $variantId: ID!, $quantity: Int!) {
    checkoutLinesAdd(checkoutId: $checkoutId, lines: [{ variantId: $variantId, quantity: $quantity }]) {
      checkout {
        id
        lines {
          id
          quantity
          variant {
            id
            name
            product {
              name
              thumbnail {
                url
              }
            }
            pricing {
              price {
                gross {
                  amount
                  currency
                }
              }
            }
          }
        }
        totalPrice {
          gross {
            amount
            currency
          }
        }
      }
      errors {
        field
        message
        code
      }
    }
  }
`;

// Checkout Mutations
export const CREATE_CHECKOUT = gql`
  mutation CreateCheckout($email: String, $channel: String, $lines: [CheckoutLineInput!]!) {
    checkoutCreate(input: { email: $email, channel: $channel, lines: $lines }) {
      checkout {
        id
        token
      }
      errors {
        field
        message
        code
      }
    }
  }
`;

export const UPDATE_CHECKOUT_LINES = gql`
  mutation UpdateCheckoutLines($checkoutId: ID!, $lines: [CheckoutLineUpdateInput!]!) {
    checkoutLinesUpdate(checkoutId: $checkoutId, lines: $lines) {
      checkout {
        id
        lines {
          id
          quantity
        }
      }
      errors {
        field
        message
        code
      }
    }
  }
`;

export const DELETE_CHECKOUT_LINES = gql`
  mutation DeleteCheckoutLines($checkoutId: ID!, $lines: [ID!]!) {
    checkoutLinesDelete(checkoutId: $checkoutId, lines: $lines) {
      checkout {
        id
        lines {
          id
        }
      }
      errors {
        field
        message
        code
      }
    }
  }
`;

export const UPDATE_CHECKOUT_SHIPPING_ADDRESS = gql`
  mutation UpdateCheckoutShippingAddress($checkoutId: ID!, $shippingAddress: AddressInput!) {
    checkoutShippingAddressUpdate(checkoutId: $checkoutId, shippingAddress: $shippingAddress) {
      checkout {
        id
        shippingAddress {
          firstName
          lastName
          streetAddress1
          city
          postalCode
          country {
            code
          }
        }
      }
      errors {
        field
        message
        code
      }
    }
  }
`;

export const UPDATE_CHECKOUT_DELIVERY_METHOD = gql`
  mutation UpdateCheckoutDeliveryMethod($checkoutId: ID!, $deliveryMethodId: ID!) {
    checkoutDeliveryMethodUpdate(id: $checkoutId, deliveryMethodId: $deliveryMethodId) {
      checkout {
        id
        delivery {
          shippingMethod {
            id
            name
          }
        }
        shippingPrice {
          gross {
            amount
            currency
          }
        }
        totalPrice {
          gross {
            amount
            currency
          }
        }
      }
      errors {
        field
        message
        code
      }
    }
  }
`;

export const COMPLETE_CHECKOUT = gql`
  mutation CompleteCheckout($checkoutId: ID!, $paymentData: PaymentInput!) {
    checkoutComplete(checkoutId: $checkoutId, paymentData: $paymentData) {
      order {
        id
        number
        status
        total {
          gross {
            amount
            currency
          }
        }
      }
      errors {
        field
        message
        code
      }
    }
  }
`;

// Address Mutations
export const CREATE_ADDRESS = gql`
  mutation CreateAddress($input: AddressInput!) {
    accountAddressCreate(input: $input) {
      address {
        id
        firstName
        lastName
        streetAddress1
        city
        postalCode
        country {
          code
        }
      }
      errors {
        field
        message
        code
      }
    }
  }
`;

export const UPDATE_ADDRESS = gql`
  mutation UpdateAddress($id: ID!, $input: AddressInput!) {
    accountAddressUpdate(id: $id, input: $input) {
      address {
        id
        firstName
        lastName
        streetAddress1
        city
        postalCode
        country {
          code
        }
      }
      errors {
        field
        message
        code
      }
    }
  }
`;

// Discount Code Mutations
export const APPLY_DISCOUNT_CODE = gql`
  mutation ApplyDiscountCode($checkoutId: ID!, $promoCode: String!) {
    checkoutAddPromoCode(checkoutId: $checkoutId, promoCode: $promoCode) {
      checkout {
        id
        discount {
          amount
          currency
        }
        totalPrice {
          gross {
            amount
            currency
          }
        }
      }
      errors {
        field
        message
        code
      }
    }
  }
`;

// Returns Mutations
export const CREATE_RETURN_REQUEST = gql`
  mutation CreateReturnRequest($input: ReturnRequestInput!) {
    returnRequestCreate(input: $input) {
      returnRequest {
        id
        status
        reason
        notes
        order {
          id
          number
        }
      }
      errors {
        field
        message
        code
      }
    }
  }
`;

// Newsletter Mutations
export const SUBSCRIBE_NEWSLETTER = gql`
  mutation SubscribeNewsletter($email: String!, $source: String) {
    newsletterSubscribe(email: $email, source: $source) {
      subscription {
        id
        email
        isActive
      }
      errors {
        field
        message
        code
      }
    }
  }
`;

