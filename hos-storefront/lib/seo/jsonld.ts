import { Product, Seller, Collection } from "@/types";

const DEFAULT_SITE_URL = "https://hos-storefront-production.up.railway.app";

function getSiteUrl() {
  return process.env.NEXT_PUBLIC_SITE_URL || DEFAULT_SITE_URL;
}

export function generateProductJSONLD(product: Product) {
  if (!product) return null;

  const imageUrl = product.thumbnail?.url || product.images?.[0]?.url;
  const price = product.defaultVariant?.pricing?.price?.gross;
  const sku = product.defaultVariant?.sku;

  const reviews =
    Array.isArray(product.reviews) && product.reviews.length
      ? product.reviews
          .filter((r) => r && (typeof r.rating === "number" || r.body || r.author))
          .slice(0, 10)
          .map((r) => ({
            "@type": "Review",
            author: r.author ? { "@type": "Person", name: r.author } : undefined,
            reviewBody: r.body,
            datePublished: r.created,
            reviewRating:
              typeof r.rating === "number"
                ? {
                    "@type": "Rating",
                    ratingValue: r.rating,
                    bestRating: 5,
                    worstRating: 1,
                  }
                : undefined,
          }))
      : undefined;

  return {
    "@context": "https://schema.org/",
    "@type": "Product",
    name: product.name,
    description: product.description,
    image: imageUrl,
    sku: sku,
    brand: product.seller
      ? {
          "@type": "Brand",
          name: product.seller.storeName,
        }
      : undefined,
    aggregateRating:
      typeof product.rating === "number"
        ? {
            "@type": "AggregateRating",
            ratingValue: product.rating,
            ratingCount: product.reviewCount,
            reviewCount: product.reviewCount,
          }
        : undefined,
    review: reviews,
    offers: price
      ? {
          "@type": "Offer",
          priceCurrency: price.currency,
          // Saleor returns Money amount as a decimal (not cents)
          price: price.amount.toFixed(2),
          availability: "https://schema.org/InStock",
          seller: product.seller
            ? {
                "@type": "Organization",
                name: product.seller.storeName,
              }
            : undefined,
          url: `${getSiteUrl()}/products/${product.slug}`,
        }
      : undefined,
  };
}

export function generateSellerJSONLD(seller: Seller) {
  if (!seller) return null;

  return {
    "@context": "https://schema.org/",
    "@type": "Store",
    name: seller.storeName,
    description: seller.description,
    image: seller.logo?.url,
    url: `${getSiteUrl()}/sellers/${seller.slug}`,
  };
}

export function generateCollectionJSONLD(collection: Collection) {
  if (!collection) return null;

  return {
    "@context": "https://schema.org/",
    "@type": "CollectionPage",
    name: collection.name,
    description: collection.description,
    image: collection.backgroundImage?.url,
  };
}

export function generateBreadcrumbJSONLD(items: Array<{ name: string; url: string }>) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      item: item.url,
    })),
  };
}


