"use client";

import { useQuery } from "@apollo/client/react";
import { GET_PRODUCT_BY_SLUG } from "@/lib/graphql/queries";
import Image from "next/image";
import { formatPrice } from "@/lib/utils";
import { Badge } from "@/components/common/Badge";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { Heart, Share2 } from "lucide-react";
import Link from "next/link";
import { useState, useEffect } from "react";
import { Loader2 } from "lucide-react";
import { AddToCartButton } from "./AddToCartButton";
import { BuyNowButton } from "./BuyNowButton";
import { InventoryDisplay } from "./InventoryDisplay";
import { generateProductJSONLD } from "@/lib/seo/jsonld";

interface ProductDetailProps {
  slug: string;
}

export function ProductDetail({ slug }: ProductDetailProps) {
  const [selectedVariant, setSelectedVariant] = useState<string | null>(null);
  const [quantity, setQuantity] = useState(1);

  const { data, loading, error } = useQuery(GET_PRODUCT_BY_SLUG, {
    variables: { slug },
    skip: !slug,
  });

  const product = (data as any)?.products?.edges?.[0]?.node;

  // Generate JSON-LD structured data.
  // Must be declared before any conditional returns to keep hook ordering stable.
  useEffect(() => {
    if (!product) {
      return;
    }
    const jsonLd = generateProductJSONLD(product as any);
    if (!jsonLd) {
      return;
    }
    const script = document.createElement("script");
    script.type = "application/ld+json";
    script.text = JSON.stringify(jsonLd);
    document.head.appendChild(script);
    return () => {
      script.parentNode?.removeChild(script);
    };
  }, [product]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive mb-4">Error loading product</p>
        <p className="text-sm text-muted-foreground">{error.message}</p>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Product not found</p>
      </div>
    );
  }

  const breadcrumbItems = [
    { label: "Products", href: "/products" },
    ...(product.collections?.[0]
      ? [{ label: product.collections[0].name, href: `/collections/${product.collections[0].slug}` }]
      : []),
    { label: product.name },
  ];

  const mainImage = product.images?.[0] || product.thumbnail;
  const price = selectedVariant
    ? product.variants?.find((v: any) => v.id === selectedVariant)?.pricing?.price?.gross
    : product.defaultVariant?.pricing?.price?.gross;

  return (
    <div>
      <Breadcrumbs items={breadcrumbItems} />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
      {/* Product Images */}
      <div>
        {mainImage ? (
          <div className="relative aspect-square overflow-hidden rounded-lg bg-gray-100 mb-4">
            <Image
              src={mainImage.url}
              alt={mainImage.alt || product.name}
              fill
              className="object-cover"
              priority
            />
          </div>
        ) : (
          <div className="aspect-square bg-gray-100 rounded-lg flex items-center justify-center">
            <span className="text-gray-400">No Image</span>
          </div>
        )}
        {product.images && product.images.length > 1 && (
          <div className="grid grid-cols-4 gap-2">
            {product.images.slice(0, 4).map((image: any, index: number) => (
              <div
                key={index}
                className="relative aspect-square overflow-hidden rounded-md bg-gray-100 cursor-pointer hover:opacity-75 transition-opacity"
              >
                <Image
                  src={image.url}
                  alt={image.alt || `${product.name} ${index + 1}`}
                  fill
                  className="object-cover"
                />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Product Information */}
      <div>
        <div className="mb-4">
          {product.seller && (
            <Link
              href={`/sellers/${product.seller.slug}`}
              className="text-sm text-primary hover:underline mb-2 inline-block"
            >
              by {product.seller.storeName}
            </Link>
          )}
          <h1 className="text-4xl font-bold mb-4">{product.name}</h1>
          {product.approvalStatus && (
            <Badge
              variant={
                product.approvalStatus === "approved"
                  ? "default"
                  : product.approvalStatus === "pending"
                  ? "secondary"
                  : "outline"
              }
              className="mb-4"
            >
              {product.approvalStatus === "approved"
                ? "✓ Approved"
                : product.approvalStatus === "pending"
                ? "⏳ Pending"
                : "Rejected"}
            </Badge>
          )}
        </div>

        {price && (
          <div className="mb-6">
            <p className="text-4xl font-bold mb-2">
              {formatPrice(price.amount, price.currency)}
            </p>
            {product.rrp && (
              <p className="text-sm text-muted-foreground">
                RRP: {formatPrice(product.rrp.amount, product.rrp.currency)}
              </p>
            )}
          </div>
        )}

        {product.description && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-2">Description</h2>
            <p className="text-muted-foreground whitespace-pre-line">{product.description}</p>
          </div>
        )}

        {/* Variant Selection */}
        {product.variants && product.variants.length > 1 && (
          <div className="mb-6">
            <h3 className="text-sm font-medium mb-2">Select Variant</h3>
            <div className="flex flex-wrap gap-2">
              {product.variants.map((variant: any) => (
                <button
                  key={variant.id}
                  onClick={() => setSelectedVariant(variant.id)}
                  className={`px-4 py-2 border rounded-md text-sm transition-colors ${
                    selectedVariant === variant.id
                      ? "border-primary bg-primary text-primary-foreground"
                      : "hover:bg-accent"
                  }`}
                >
                  {variant.name}
                  {variant.pricing?.price?.gross && (
                    <span className="ml-2">
                      {formatPrice(variant.pricing.price.gross.amount, variant.pricing.price.gross.currency)}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Real-Time Inventory Display */}
        <div className="mb-6">
          <InventoryDisplay product={product} selectedVariant={selectedVariant} />
        </div>

        {/* Quantity Selection */}
        <div className="mb-6">
          <label className="text-sm font-medium mb-2 block">Quantity</label>
          <div className="flex items-center gap-4">
            <button
              onClick={() => setQuantity(Math.max(1, quantity - 1))}
              className="px-3 py-1 border rounded-md hover:bg-accent transition-all duration-200 active:scale-95"
            >
              -
            </button>
            <span className="w-12 text-center font-semibold">{quantity}</span>
            <button
              onClick={() => setQuantity(quantity + 1)}
              className="px-3 py-1 border rounded-md hover:bg-accent transition-all duration-200 active:scale-95"
            >
              +
            </button>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 mb-6">
          <AddToCartButton
            variantId={selectedVariant || product.defaultVariant?.id || product.variants?.[0]?.id}
            quantity={quantity}
            productName={product.name}
          />
          <BuyNowButton
            variantId={selectedVariant || product.defaultVariant?.id || product.variants?.[0]?.id}
            quantity={quantity}
            productName={product.name}
          />
          <button className="px-6 py-3 border rounded-md hover:bg-accent transition-colors">
            <Heart className="h-5 w-5" />
          </button>
          <button className="px-6 py-3 border rounded-md hover:bg-accent transition-colors">
            <Share2 className="h-5 w-5" />
          </button>
        </div>

        {/* SKU Display */}
        {selectedVariant && product.variants && (
          <div className="mb-6">
            <p className="text-sm text-muted-foreground">
              SKU: <span className="font-mono font-semibold text-foreground">
                {product.variants.find((v: any) => v.id === selectedVariant)?.sku || "N/A"}
              </span>
            </p>
          </div>
        )}

        {/* Country-Specific Pricing */}
        {product.countrySpecificPricing && Object.keys(product.countrySpecificPricing).length > 0 && (
          <div className="mb-6 border rounded-lg p-4 bg-secondary/50">
            <h3 className="text-sm font-semibold mb-3">Country-Specific Pricing</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              {Object.entries(product.countrySpecificPricing).map(([country, price]: [string, any]) => (
                <div key={country} className="flex justify-between">
                  <span className="text-muted-foreground">{country.toUpperCase()}:</span>
                  <span className="font-semibold">
                    {formatPrice(price, price?.currency || "USD")}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Seller Information */}
        {product.seller && (
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold mb-4">Seller Information</h3>
            <div className="flex items-center gap-4">
              {product.seller.logo && (
                <div className="relative w-16 h-16 rounded-full overflow-hidden bg-gray-100">
                  <Image
                    src={product.seller.logo.url}
                    alt={product.seller.storeName}
                    fill
                    className="object-cover"
                  />
                </div>
              )}
              <div>
                <Link
                  href={`/sellers/${product.seller.slug}`}
                  className="font-semibold hover:text-primary transition-colors"
                >
                  {product.seller.storeName}
                </Link>
                {product.seller.sellerType && (
                  <p className="text-sm text-muted-foreground">
                    {product.seller.sellerType === "b2b_wholesale"
                      ? "B2B Wholesale"
                      : product.seller.sellerType === "b2c_retail"
                      ? "B2C Retail"
                      : "B2B & B2C"}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Collections */}
        {product.collections && product.collections.length > 0 && (
          <div className="border-t pt-6 mt-6">
            <h3 className="text-lg font-semibold mb-4">Collections</h3>
            <div className="flex flex-wrap gap-2">
              {product.collections.map((collection: any) => (
                <Link
                  key={collection.id}
                  href={`/collections/${collection.slug}`}
                  className="px-3 py-1 bg-secondary text-secondary-foreground rounded-md text-sm hover:bg-secondary/80 transition-colors"
                >
                  {collection.name}
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
    </div>
  );
}

