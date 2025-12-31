"use client";

import { useQuery } from "@apollo/client/react";
import { GET_FEATURED_PRODUCTS } from "@/lib/graphql/queries";
import Link from "next/link";
import Image from "next/image";
import { formatPrice } from "@/lib/utils";
import { ProductCard } from "./ProductCard";

export function FeaturedProducts() {
  const { data, loading, error } = useQuery(GET_FEATURED_PRODUCTS, {
    variables: { first: 8 },
    errorPolicy: "all", // Continue even if there are errors
  });

  if (loading) {
    return (
      <section>
        <h2 className="text-3xl font-bold mb-8">Featured Products</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-gray-200 aspect-square rounded-lg mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </section>
    );
  }

  if (error) {
    console.error("FeaturedProducts GraphQL Error:", error);
    console.error("Error details:", {
      message: error.message,
      graphQLErrors: error.graphQLErrors,
      networkError: error.networkError,
    });
    return (
      <section>
        <h2 className="text-3xl font-bold mb-8">Featured Products</h2>
        <p className="text-muted-foreground">Error loading products. Please try again later.</p>
        {process.env.NODE_ENV === "development" && (
          <p className="text-xs text-red-500 mt-2">{error.message}</p>
        )}
      </section>
    );
  }

  const products = (data as any)?.featuredProducts?.edges?.map((edge: any) => edge.node) || [];

  return (
    <section>
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-3xl font-bold">Featured Products</h2>
        <Link
          href="/products"
          className="text-primary hover:underline font-medium"
        >
          View All →
        </Link>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {products.map((product: any) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
      {products.length === 0 && (
        <p className="text-center text-muted-foreground py-12">
          No featured products available at the moment.
        </p>
      )}
    </section>
  );
}

