"use client";

import { useQuery } from "@apollo/client/react";
import { GET_SELLERS } from "@/lib/graphql/queries";
import { SellerCard } from "./SellerCard";
import { Loader2 } from "lucide-react";
import { useState } from "react";

export function SellerListing() {
  const [filter, setFilter] = useState<"all" | "b2b" | "b2c" | "hybrid">("all");
  const { data, loading, error, fetchMore } = useQuery(GET_SELLERS, {
    variables: { first: 24 },
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
        <p className="text-destructive mb-4">Error loading sellers</p>
        <p className="text-sm text-muted-foreground">{error.message}</p>
      </div>
    );
  }

  let sellers = (data as any)?.sellers?.edges?.map((edge: any) => edge.node) || [];
  const pageInfo = (data as any)?.sellers?.pageInfo;

  // Apply filter
  if (filter !== "all") {
    sellers = sellers.filter((seller: any) => {
      if (filter === "b2b") return seller.sellerType === "b2b_wholesale";
      if (filter === "b2c") return seller.sellerType === "b2c_retail";
      if (filter === "hybrid") return seller.sellerType === "hybrid";
      return true;
    });
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <p className="text-sm text-muted-foreground">
          {sellers.length} {sellers.length === 1 ? "seller" : "sellers"} found
        </p>
        <div className="flex gap-2">
          <button
            onClick={() => setFilter("all")}
            className={`px-4 py-2 rounded-md text-sm transition-colors ${
              filter === "all"
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter("b2c")}
            className={`px-4 py-2 rounded-md text-sm transition-colors ${
              filter === "b2c"
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
            }`}
          >
            B2C Retail
          </button>
          <button
            onClick={() => setFilter("b2b")}
            className={`px-4 py-2 rounded-md text-sm transition-colors ${
              filter === "b2b"
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
            }`}
          >
            B2B Wholesale
          </button>
          <button
            onClick={() => setFilter("hybrid")}
            className={`px-4 py-2 rounded-md text-sm transition-colors ${
              filter === "hybrid"
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
            }`}
          >
            Hybrid
          </button>
        </div>
      </div>

      {sellers.length > 0 ? (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {sellers.map((seller: any) => (
              <SellerCard key={seller.id} seller={seller} />
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
          <p className="text-muted-foreground">No sellers found.</p>
        </div>
      )}
    </div>
  );
}

