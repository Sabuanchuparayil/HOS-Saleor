"use client";

import { useQuery } from "@apollo/client/react";
import { GET_SELLER, GET_PRODUCTS } from "@/lib/graphql/queries";
import Image from "next/image";
import { ProductCard } from "@/components/product/ProductCard";
import { Badge } from "@/components/common/Badge";
import { formatPrice } from "@/lib/utils";
import { Loader2, Store, Package, TrendingUp } from "lucide-react";

interface SellerStorefrontProps {
  slug: string;
}

export function SellerStorefront({ slug }: SellerStorefrontProps) {
  const { data: sellerData, loading: sellerLoading } = useQuery(GET_SELLER, {
    variables: { slug },
  });

  const seller = (sellerData as any)?.seller;

  const { data: productsData, loading: productsLoading } = useQuery(GET_PRODUCTS, {
    variables: {
      first: 100, // Get more products to filter client-side
    },
    skip: !seller,
  });

  // Filter products by seller client-side until backend supports seller filtering
  let sellerProducts = (productsData as any)?.products?.edges?.map((edge: any) => edge.node) || [];
  if (seller) {
    sellerProducts = sellerProducts.filter(
      (product: any) => product.seller?.id === seller.id
    );
  }

  if (sellerLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!seller) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Seller not found</p>
      </div>
    );
  }

  const products = (productsData as any)?.products?.edges?.map((edge: any) => edge.node) || [];
  const sellerTypeLabels: Record<string, string> = {
    b2b_wholesale: "B2B Wholesale",
    b2c_retail: "B2C Retail",
    hybrid: "B2B & B2C",
  };

  return (
    <div>
      {/* Seller Header */}
      <div className="bg-gradient-to-r from-purple-900 to-indigo-900 text-white rounded-lg p-8 mb-8">
        <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
          {seller.logo ? (
            <div className="relative w-24 h-24 rounded-full overflow-hidden bg-white/20 border-4 border-white/30">
              <Image
                src={seller.logo.url}
                alt={seller.storeName}
                fill
                className="object-cover"
              />
            </div>
          ) : (
            <div className="w-24 h-24 rounded-full bg-white/20 border-4 border-white/30 flex items-center justify-center">
              <Store className="h-12 w-12" />
            </div>
          )}
          <div className="flex-1 text-center md:text-left">
            <h1 className="text-4xl font-bold mb-2">{seller.storeName}</h1>
            {seller.sellerType && (
              <Badge variant="secondary" className="mb-4 bg-white/20 text-white border-white/30">
                {sellerTypeLabels[seller.sellerType] || seller.sellerType}
              </Badge>
            )}
            {seller.description && (
              <p className="text-lg text-white/90 max-w-2xl">{seller.description}</p>
            )}
          </div>
        </div>

        {/* Seller Stats */}
        {seller.analytics && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8 pt-8 border-t border-white/20">
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Package className="h-5 w-5" />
                <span className="text-2xl font-bold">{seller.analytics.orderCount || 0}</span>
              </div>
              <p className="text-sm text-white/80">Total Orders</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <TrendingUp className="h-5 w-5" />
                <span className="text-2xl font-bold">
                  {seller.analytics.revenue
                    ? new Intl.NumberFormat("en-US", {
                        style: "currency",
                        currency: seller.analytics.revenue.currency,
                        notation: "compact",
                      }).format(seller.analytics.revenue.amount)
                    : "$0"}
                </span>
              </div>
              <p className="text-sm text-white/80">Total Revenue</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <span className="text-2xl font-bold">
                  {seller.analytics.earnings
                    ? new Intl.NumberFormat("en-US", {
                        style: "currency",
                        currency: seller.analytics.earnings.currency,
                        notation: "compact",
                      }).format(seller.analytics.earnings.amount)
                    : "$0"}
                </span>
              </div>
              <p className="text-sm text-white/80">Total Earnings</p>
            </div>
          </div>
        )}
      </div>

      {/* Seller Products */}
      <div>
        <h2 className="text-2xl font-bold mb-6">Products from {seller.storeName}</h2>
        {productsLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : sellerProducts.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {sellerProducts.map((product: any) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No products available from this seller.</p>
          </div>
        )}
      </div>
    </div>
  );
}

