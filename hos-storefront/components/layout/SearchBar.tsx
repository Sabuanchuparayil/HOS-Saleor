"use client";

import { useState, useRef, useEffect } from "react";
import { useQuery } from "@apollo/client/react";
import { SEARCH_PRODUCTS } from "@/lib/graphql/queries";
import { Search, X, Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export function SearchBar() {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  const { data, loading } = useQuery(SEARCH_PRODUCTS, {
    variables: { query, first: 5 },
    skip: !query || query.length < 2,
  });

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowResults(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
      setShowResults(false);
      setIsOpen(false);
    }
  };

  const products = (data as any)?.products?.edges?.map((edge: any) => edge.node) || [];
  const sellers = (data as any)?.sellers?.edges?.map((edge: any) => edge.node) || [];

  return (
    <div ref={searchRef} className="relative flex-1 max-w-2xl">
      <form onSubmit={handleSearch} className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setShowResults(e.target.value.length >= 2);
          }}
          onFocus={() => setShowResults(query.length >= 2)}
          placeholder="Search products, sellers..."
          className="w-full px-4 py-2 pl-10 pr-10 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
        {query && (
          <button
            type="button"
            onClick={() => {
              setQuery("");
              setShowResults(false);
            }}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 hover:bg-accent rounded"
          >
            <X className="h-4 w-4 text-muted-foreground" />
          </button>
        )}
      </form>

      {showResults && (products.length > 0 || sellers.length > 0 || loading) && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-background border rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
          {loading ? (
            <div className="p-4 flex items-center justify-center">
              <Loader2 className="h-5 w-5 animate-spin text-primary" />
            </div>
          ) : (
            <>
              {products.length > 0 && (
                <div className="p-2">
                  <h3 className="px-3 py-2 text-sm font-semibold text-muted-foreground">
                    Products
                  </h3>
                  {products.map((product: any) => (
                    <Link
                      key={product.id}
                      href={`/products/${product.slug}`}
                      onClick={() => {
                        setShowResults(false);
                        setQuery("");
                      }}
                      className="flex items-center gap-3 px-3 py-2 hover:bg-accent rounded-md transition-colors"
                    >
                      {product.thumbnail && (
                        <div className="relative w-12 h-12 rounded-md overflow-hidden bg-gray-100 flex-shrink-0">
                          <img
                            src={product.thumbnail.url}
                            alt={product.thumbnail.alt || product.name}
                            className="w-full h-full object-cover"
                          />
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{product.name}</p>
                        {product.seller && (
                          <p className="text-xs text-muted-foreground">
                            by {product.seller.storeName}
                          </p>
                        )}
                      </div>
                    </Link>
                  ))}
                </div>
              )}

              {sellers.length > 0 && (
                <div className="p-2 border-t">
                  <h3 className="px-3 py-2 text-sm font-semibold text-muted-foreground">
                    Sellers
                  </h3>
                  {sellers.map((seller: any) => (
                    <Link
                      key={seller.id}
                      href={`/sellers/${seller.slug}`}
                      onClick={() => {
                        setShowResults(false);
                        setQuery("");
                      }}
                      className="flex items-center gap-3 px-3 py-2 hover:bg-accent rounded-md transition-colors"
                    >
                      {seller.logo && (
                        <div className="relative w-12 h-12 rounded-full overflow-hidden bg-gray-100 flex-shrink-0">
                          <img
                            src={seller.logo.url}
                            alt={seller.storeName}
                            className="w-full h-full object-cover"
                          />
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{seller.storeName}</p>
                        <p className="text-xs text-muted-foreground truncate">
                          {seller.description || "Seller"}
                        </p>
                      </div>
                    </Link>
                  ))}
                </div>
              )}

              {products.length === 0 && sellers.length === 0 && (
                <div className="p-4 text-center text-muted-foreground">
                  No results found
                </div>
              )}

              {(products.length > 0 || sellers.length > 0) && (
                <div className="p-2 border-t">
                  <Link
                    href={`/search?q=${encodeURIComponent(query)}`}
                    onClick={() => {
                      setShowResults(false);
                      setIsOpen(false);
                    }}
                    className="block px-3 py-2 text-sm text-primary hover:bg-accent rounded-md text-center font-medium"
                  >
                    View all results →
                  </Link>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

