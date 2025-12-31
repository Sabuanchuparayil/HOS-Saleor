"use client";

import { useState } from "react";
import { X } from "lucide-react";

interface ProductFiltersProps {
  filters: {
    category: string | null;
    seller: string | null;
    priceRange: { min: number; max: number } | null;
  };
  onFiltersChange: (filters: any) => void;
}

export function ProductFilters({ filters, onFiltersChange }: ProductFiltersProps) {
  const [priceMin, setPriceMin] = useState(filters.priceRange?.min?.toString() || "");
  const [priceMax, setPriceMax] = useState(filters.priceRange?.max?.toString() || "");

  const handlePriceFilter = () => {
    const min = priceMin ? parseFloat(priceMin) : undefined;
    const max = priceMax ? parseFloat(priceMax) : undefined;
    onFiltersChange({
      ...filters,
      priceRange: min || max ? { min: min || 0, max: max || 10000 } : null,
    });
  };

  const clearFilters = () => {
    onFiltersChange({
      category: null,
      seller: null,
      priceRange: null,
    });
    setPriceMin("");
    setPriceMax("");
  };

  const hasActiveFilters = filters.category || filters.seller || filters.priceRange;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Filters</h2>
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="text-sm text-primary hover:underline flex items-center gap-1"
          >
            <X className="h-4 w-4" />
            Clear all
          </button>
        )}
      </div>

      <div>
        <h3 className="text-sm font-medium mb-3">Price Range</h3>
        <div className="space-y-2">
          <div className="flex gap-2">
            <input
              type="number"
              placeholder="Min"
              value={priceMin}
              onChange={(e) => setPriceMin(e.target.value)}
              className="w-full px-3 py-2 border rounded-md text-sm"
            />
            <input
              type="number"
              placeholder="Max"
              value={priceMax}
              onChange={(e) => setPriceMax(e.target.value)}
              className="w-full px-3 py-2 border rounded-md text-sm"
            />
          </div>
          <button
            onClick={handlePriceFilter}
            className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm hover:bg-primary/90"
          >
            Apply
          </button>
        </div>
      </div>

      {/* Additional filters can be added here */}
      <div>
        <h3 className="text-sm font-medium mb-3">Seller Type</h3>
        <div className="space-y-2">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              className="rounded"
              checked={filters.seller === "b2c"}
              onChange={(e) =>
                onFiltersChange({
                  ...filters,
                  seller: e.target.checked ? "b2c" : null,
                })
              }
            />
            <span className="text-sm">B2C Retail</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              className="rounded"
              checked={filters.seller === "b2b"}
              onChange={(e) =>
                onFiltersChange({
                  ...filters,
                  seller: e.target.checked ? "b2b" : null,
                })
              }
            />
            <span className="text-sm">B2B Wholesale</span>
          </label>
        </div>
      </div>
    </div>
  );
}

