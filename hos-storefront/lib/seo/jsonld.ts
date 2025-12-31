import { Product, Seller, Collection } from "@/types";

export function generateProductJSONLD(product: Product) {
  if (!product) return null;

  return {
    "@context": "https://schema.org/",
    "@type": "Product",
    name: product.name,
    description: product.description,
    image: product.thumbnail?.url || product.images?.[0]?.url,
    brand: product.seller
      ? {
          "@type": "Brand",
          name: product.seller.storeName,
        }
      : undefined,
    offers: product.defaultVariant?.pricing?.price?.gross
      ? {
          "@type": "Offer",
          priceCurrency: product.defaultVariant.pricing.price.gross.currency,
          price: (product.defaultVariant.pricing.price.gross.amount / 100).toFixed(2),
          availability: "https://schema.org/InStock",
          seller: product.seller
            ? {
                "@type": "Organization",
                name: product.seller.storeName,
              }
            : undefined,
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
    url: `${process.env.NEXT_PUBLIC_SITE_URL}/sellers/${seller.slug}`,
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

