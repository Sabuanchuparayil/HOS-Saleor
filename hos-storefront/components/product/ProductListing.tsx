"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useQuery } from "@apollo/client/react";
import { GET_PRODUCTS } from "@/lib/graphql/queries";
import { ProductCard } from "./ProductCard";
import { ProductFilters } from "./ProductFilters";
import { Loader2 } from "lucide-react";

export function ProductListing() {
  const [filters, setFilters] = useState({
    category: null as string | null,
    seller: null as string | null,
    priceRange: null as { min: number; max: number } | null,
  });
  const [sortBy, setSortBy] = useState("RELEVANCE");
  const [page, setPage] = useState(1);
  const itemsPerPage = 24;

  const { data, loading, error, fetchMore } = useQuery(GET_PRODUCTS, {
    variables: {
      first: itemsPerPage,
      filter: {
        ...(filters.category && { categories: [filters.category] }),
        ...(filters.priceRange && {
          price: {
            gte: filters.priceRange.min,
            lte: filters.priceRange.max,
          },
        }),
      },
      sortBy: {
        field: sortBy === "PRICE" ? "PRICE" : "NAME",
        direction: sortBy === "PRICE_DESC" ? "DESC" : "ASC",
      },
    },
    notifyOnNetworkStatusChange: true,
  });

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive mb-4">Error loading products</p>
        <p className="text-sm text-muted-foreground">{error.message}</p>
      </div>
    );
  }

  const products = (data as any)?.products?.edges?.map((edge: any) => edge.node) || [];
  const pageInfo = (data as any)?.products?.pageInfo;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
      <aside className="lg:col-span-1">
        <ProductFilters filters={filters} onFiltersChange={setFilters} />
      </aside>
      <div className="lg:col-span-3">
        <div className="flex items-center justify-between mb-6">
          <p className="text-sm text-muted-foreground">
            {products.length} {products.length === 1 ? "product" : "products"} found
          </p>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-4 py-2 border rounded-md bg-background"
          >
            <option value="RELEVANCE">Relevance</option>
            <option value="NAME">Name A-Z</option>
            <option value="PRICE">Price: Low to High</option>
            <option value="PRICE_DESC">Price: High to Low</option>
          </select>
        </div>
        {products.length > 0 ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {products.map((product: any, index: number) => (
                <div
                  key={product.id}
                  className="animate-fade-in"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <ProductCard product={product} />
                </div>
              ))}
            </div>
            {pageInfo?.hasNextPage && (
              <div className="mt-8 text-center">
                <button
                  onClick={() => {
                    fetchMore({
                      variables: {
                        after: pageInfo.endCursor,
                      },
                    });
                    setPage(page + 1);
                  }}
                  disabled={loading}
                  className="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
                >
                  {loading ? "Loading..." : "Load More"}
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No products found matching your filters.</p>
          </div>
        )}
      </div>
    </div>
  );
}

