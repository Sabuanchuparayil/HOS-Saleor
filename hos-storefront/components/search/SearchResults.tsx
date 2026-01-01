"use client";

import { useState } from "react";
import { useQuery } from "@apollo/client/react";
import { SEARCH_PRODUCTS, SEARCH_SELLERS } from "@/lib/graphql/queries";
import { ProductCard } from "@/components/product/ProductCard";
import { SellerCard } from "@/components/seller/SellerCard";
import { Loader2 } from "lucide-react";
import { SearchBar } from "@/components/layout/SearchBar";

interface SearchResultsProps {
  query: string;
}

export function SearchResults({ query }: SearchResultsProps) {
  const [activeTab, setActiveTab] = useState<"all" | "products" | "sellers">("all");
  const [sellerFilter, setSellerFilter] = useState<string | null>(null);

  const { data: productsData, loading: productsLoading } = useQuery(SEARCH_PRODUCTS, {
    variables: { query, first: 24 },
    skip: !query || query.length < 2,
  });

  const { data: sellersData, loading: sellersLoading } = useQuery(SEARCH_SELLERS, {
    variables: { query, first: 12 },
    skip: !query || query.length < 2,
  });

  const products = (productsData as any)?.products?.edges?.map((edge: any) => edge.node) || [];
  const sellers = (sellersData as any)?.sellers?.edges?.map((edge: any) => edge.node) || [];
  const loading = productsLoading || sellersLoading;
  const filteredProducts = sellerFilter
    ? products.filter((p: any) => p?.seller?.id === sellerFilter)
    : products;

  if (!query || query.length < 2) {
    return (
      <div>
        <h1 className="text-4xl font-bold mb-8">Search</h1>
        <div className="mb-8">
          <SearchBar />
        </div>
        <div className="text-center py-12">
          <p className="text-muted-foreground">
            Enter at least 2 characters to search
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">
          Search Results for "{query}"
        </h1>
        <div className="mb-6">
          <SearchBar />
        </div>
        
        {/* Seller Filter */}
        {sellers.length > 0 && activeTab === "products" && (
          <div className="mb-4">
            <label className="text-sm font-medium mb-2 block">Filter by Seller:</label>
            <select
              value={sellerFilter || ""}
              onChange={(e) => setSellerFilter(e.target.value || null)}
              className="px-4 py-2 border rounded-md bg-background text-sm"
            >
              <option value="">All Sellers</option>
              {sellers.map((seller: any) => (
                <option key={seller.id} value={seller.id}>
                  {seller.storeName}
                </option>
              ))}
            </select>
          </div>
        )}

        <div className="flex gap-2 border-b">
          <button
            onClick={() => setActiveTab("all")}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === "all"
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            All ({filteredProducts.length + sellers.length})
          </button>
          <button
            onClick={() => setActiveTab("products")}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === "products"
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Products ({filteredProducts.length})
          </button>
          <button
            onClick={() => setActiveTab("sellers")}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === "sellers"
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Sellers ({sellers.length})
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : (
        <>
          {(activeTab === "all" || activeTab === "products") && (
            <div className={activeTab === "all" ? "mb-12" : ""}>
              <h2 className="text-2xl font-bold mb-6">Products</h2>
              {filteredProducts.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                  {filteredProducts.map((product: any) => (
                    <ProductCard key={product.id} product={product} />
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No products found</p>
              )}
            </div>
          )}

          {(activeTab === "all" || activeTab === "sellers") && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Sellers</h2>
              {sellers.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                  {sellers.map((seller: any) => (
                    <SellerCard key={seller.id} seller={seller} />
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No sellers found</p>
              )}
            </div>
          )}

          {filteredProducts.length === 0 && sellers.length === 0 && (
            <div className="text-center py-12">
              <p className="text-muted-foreground mb-4">
                No results found for "{query}"
              </p>
              <p className="text-sm text-muted-foreground">
                Try different keywords or browse our products
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

