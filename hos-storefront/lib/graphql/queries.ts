import { gql } from "@apollo/client";

// Product Queries
export const GET_PRODUCTS = gql`
  query GetProducts(
    $first: Int
    $after: String
    $filter: ProductFilterInput
    $sortBy: ProductOrder
    $channel: String
  ) {
    products(
      first: $first
      after: $after
      filter: $filter
      sortBy: $sortBy
      channel: $channel
    ) {
      edges {
        node {
          id
          name
          slug
          description
          seoTitle
          seoDescription
          rating
          defaultVariant {
            id
            name
            pricing {
              price {
                gross {
                  amount
                  currency
                }
                net {
                  amount
                  currency
                }
              }
            }
          }
          thumbnail {
            url
            alt
          }
          seller {
            id
            storeName
            slug
            logo {
              url
            }
          }
          approvalStatus
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
    }
  }
`;

export const GET_PRODUCT_BY_SLUG = gql`
  query GetProductBySlug($slug: String!, $channel: String) {
    products(first: 1, filter: { slugs: [$slug] }, channel: $channel) {
      edges {
        node {
          id
          name
          slug
          description
          seoTitle
          seoDescription
          rating
          seller {
            id
            storeName
            slug
            description
            logo {
              url
            }
            sellerType
          }
          approvalStatus
          rrp {
            amount
            currency
          }
          variants {
            id
            name
            sku
            stockQuantity
            isAvailable
            pricing {
              price {
                gross {
                  amount
                  currency
                }
                net {
                  amount
                  currency
                }
              }
            }
          }
          images {
            url
            alt
          }
          collections {
            id
            name
            slug
          }
          countrySpecificPricing
          countrySpecificStock
          complianceData
          isExclusiveToSeller
        }
      }
    }
  }
`;

export const GET_PRODUCT = gql`
  query GetProduct($id: ID!, $channel: String) {
    product(id: $id, channel: $channel) {
      id
      name
      slug
      description
      seoTitle
      seoDescription
      rating
      seller {
        id
        storeName
        slug
        description
        logo {
          url
        }
        sellerType
      }
      approvalStatus
      rrp {
        amount
        currency
      }
      variants {
        id
        name
        sku
        pricing {
          price {
            gross {
              amount
              currency
            }
            net {
              amount
              currency
            }
          }
        }
      }
      images {
        url
        alt
      }
      collections {
        id
        name
        slug
      }
    }
  }
`;

// Seller Queries
export const GET_SELLERS = gql`
  query GetSellers($first: Int, $after: String) {
    sellers(first: $first, after: $after) {
      edges {
        node {
          id
          storeName
          slug
          description
          logo {
            url
          }
          sellerType
          status
          analytics {
            revenue {
              amount
              currency
            }
            earnings {
              amount
              currency
            }
            orderCount
          }
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
    }
  }
`;

export const GET_SELLER = gql`
  query GetSeller($id: ID, $slug: String) {
    seller(id: $id, slug: $slug) {
      id
      storeName
      slug
      description
      logo {
        url
      }
      sellerType
      status
      analytics {
        revenue {
          amount
          currency
        }
        earnings {
          amount
          currency
        }
        orderCount
      }
    }
  }
`;

// Homepage Queries
export const GET_FEATURED_PRODUCTS = gql`
  query GetFeaturedProducts($channel: String, $first: Int) {
    featuredProducts(channel: $channel, first: $first) {
      edges {
        node {
          id
          name
          slug
          defaultVariant {
            pricing {
              price {
                gross {
                  amount
                  currency
                }
              }
            }
          }
          thumbnail {
            url
            alt
          }
          seller {
            storeName
            logo {
              url
            }
          }
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
    }
  }
`;

export const GET_FEATURED_COLLECTIONS = gql`
  query GetFeaturedCollections($channel: String, $first: Int) {
    featuredCollections(channel: $channel, first: $first) {
      edges {
        node {
          id
          name
          slug
          description
          backgroundImage {
            url
            alt
          }
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
    }
  }
`;

export const GET_COLLECTION = gql`
  query GetCollection($slug: String!, $channel: String) {
    collection(slug: $slug, channel: $channel) {
      id
      name
      slug
      description
      backgroundImage {
        url
        alt
      }
      products(first: 50, channel: $channel) {
        edges {
          node {
            id
            name
            slug
            description
            thumbnail {
              url
              alt
            }
            defaultVariant {
              pricing {
                price {
                  gross {
                    amount
                    currency
                  }
                }
              }
            }
            seller {
              id
              storeName
              slug
              logo {
                url
              }
            }
          }
        }
      }
    }
  }
`;

// Checkout Queries
export const GET_CHECKOUT = gql`
  query GetCheckout($id: ID!) {
    checkout(id: $id) {
      id
      token
      email
      isShippingRequired
      channel {
        slug
      }
      lines {
        id
        quantity
        totalPrice {
          gross {
            amount
            currency
          }
        }
        variant {
          id
          name
          sku
          product {
            id
            name
            slug
            thumbnail {
              url
              alt
            }
            seller {
              id
              storeName
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
      subtotalPrice {
        gross {
          amount
          currency
        }
      }
      shippingPrice {
        gross {
          amount
          currency
        }
      }
      shippingMethods {
        id
        name
        minimumDeliveryDays
        maximumDeliveryDays
        price {
          amount
          currency
        }
      }
      delivery {
        shippingMethod {
          id
          name
          price {
            amount
            currency
          }
        }
      }
      totalPrice {
        gross {
          amount
          currency
        }
        tax {
          amount
          currency
        }
      }
      discount {
        amount
        currency
      }
      shippingAddress {
        firstName
        lastName
        streetAddress1
        streetAddress2
        city
        postalCode
        country {
          code
        }
        phone
      }
    }
  }
`;



// Order Queries
export const GET_ORDER = gql`
  query GetOrder($id: ID!) {
    order(id: $id) {
      id
      number
      status
      created
      subtotal {
        gross {
          amount
          currency
        }
      }
      shippingPrice {
        gross {
          amount
          currency
        }
      }
      total {
        gross {
          amount
          currency
        }
        tax {
          amount
          currency
        }
      }
      shippingAddress {
        firstName
        lastName
        streetAddress1
        streetAddress2
        city
        postalCode
        country {
          code
        }
        phone
      }
      lines {
        id
        quantity
        totalPrice {
          gross {
            amount
            currency
          }
        }
        variant {
          id
          name
          product {
            id
            name
            slug
            thumbnail {
              url
              alt
            }
            seller {
              id
              storeName
              slug
            }
          }
        }
        seller {
          id
          storeName
          slug
          logo {
            url
          }
        }
        sellerName
      }
    }
  }
`;

// User Account Queries
export const GET_USER_ORDERS = gql`
  query GetUserOrders($first: Int, $after: String) {
    me {
      id
      email
      orders(first: $first, after: $after) {
        totalCount
        edges {
          node {
            id
            number
            status
            created
            total {
              gross {
                amount
                currency
              }
            }
            lines {
              id
            }
          }
        }
        pageInfo {
          hasNextPage
          hasPreviousPage
          startCursor
          endCursor
        }
      }
    }
  }
`;

export const GET_USER_ADDRESSES = gql`
  query GetUserAddresses {
    me {
      id
      addresses {
        id
        firstName
        lastName
        streetAddress1
        streetAddress2
        city
        postalCode
        countryArea
        country {
          code
          name
        }
        phone
        isDefaultShipping
        isDefaultBilling
      }
    }
  }
`;

// Search Queries
export const SEARCH_PRODUCTS = gql`
  query SearchProducts($query: String!, $first: Int, $after: String) {
    products(first: $first, after: $after, filter: { search: $query }) {
      edges {
        node {
          id
          name
          slug
          description
          thumbnail {
            url
            alt
          }
          defaultVariant {
            pricing {
              price {
                gross {
                  amount
                  currency
                }
              }
            }
          }
          seller {
            id
            storeName
            slug
            logo {
              url
            }
          }
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
    }
  }
`;

export const SEARCH_SELLERS = gql`
  query SearchSellers($query: String!, $first: Int, $after: String) {
    sellers(first: $first, after: $after, filter: { search: $query }) {
      edges {
        node {
          id
          storeName
          slug
          description
          logo {
            url
          }
          sellerType
          status
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
    }
  }
`;

// Returns Queries
export const GET_USER_RETURNS = gql`
  query GetUserReturns($first: Int, $after: String) {
    me {
      id
      returnRequests(first: $first, after: $after) {
        edges {
          node {
            id
            status
            reason
            notes
            requestedAt
            order {
              id
              number
            }
            orderId
          }
        }
        pageInfo {
          hasNextPage
          hasPreviousPage
          startCursor
          endCursor
        }
      }
    }
  }
`;

// Loyalty Queries (Optional - may not be available in all Saleor instances)
export const GET_LOYALTY_BALANCE = gql`
  query GetLoyaltyBalance {
    loyaltyPointsBalance {
      id
      balance
      user {
        id
        email
      }
    }
  }
`;

export const GET_LOYALTY_TRANSACTIONS = gql`
  query GetLoyaltyTransactions($first: Int, $after: String) {
    loyaltyPointsTransactions(first: $first, after: $after) {
      edges {
        node {
          id
          points
          transactionType
          description
          created
          order {
            id
            number
          }
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
    }
  }
`;

export const GET_USER_BADGES = gql`
  query GetUserBadges($first: Int) {
    userBadges(first: $first) {
      edges {
        node {
          id
          badge {
            id
            name
            description
            icon
          }
          earnedAt
        }
      }
    }
  }
`;

export const GET_REWARDS = gql`
  query GetRewards($first: Int) {
    rewards(first: $first, isActive: true) {
      edges {
        node {
          id
          name
          description
          pointsRequired
          discountType
          discountValue
          isActive
        }
      }
    }
  }
`;

// Discount/Promotion Queries
export const GET_PROMOTIONS = gql`
  query GetPromotions($first: Int, $after: String) {
    promotions(first: $first, after: $after) {
      edges {
        node {
          id
          name
          description
          startDate
          endDate
          rules {
            id
            rewardValueType
            rewardValue
            cataloguePredicate
          }
          seller {
            id
            storeName
            slug
          }
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
    }
  }
`;

export const GET_VOUCHERS = gql`
  query GetVouchers($first: Int, $after: String) {
    vouchers(first: $first, after: $after) {
      edges {
        node {
          id
          name
          code
          description
          discountValueType
          discountValue
          startDate
          endDate
          isActive
          seller {
            id
            storeName
            slug
          }
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
    }
  }
`;

