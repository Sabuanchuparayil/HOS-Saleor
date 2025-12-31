"use client";

import { useState, useEffect } from "react";
import { Package, MapPin, AlertCircle, CheckCircle2 } from "lucide-react";
import { Badge } from "@/components/common/Badge";

interface InventoryDisplayProps {
  product: any;
  selectedVariant?: string | null;
}

export function InventoryDisplay({ product, selectedVariant }: InventoryDisplayProps) {
  const [currentCountry, setCurrentCountry] = useState<string>("US");

  // Get variant stock information
  const variant = product.variants?.find((v: any) => v.id === selectedVariant) || 
                  product.defaultVariant || 
                  product.variants?.[0];

  const stockQuantity = variant?.stockQuantity || 0;
  const isAvailable = variant?.isAvailable ?? (stockQuantity > 0);
  
  // Get country-specific stock if available
  const countryStock = product.countrySpecificStock?.[currentCountry] || null;
  const displayStock = countryStock !== null ? countryStock : stockQuantity;

  // Determine stock status
  const getStockStatus = () => {
    if (displayStock === null || displayStock === undefined) {
      return { status: "unknown", label: "Stock Unknown", color: "secondary" };
    }
    if (displayStock > 10) {
      return { status: "in_stock", label: "In Stock", color: "default" };
    }
    if (displayStock > 0) {
      return { status: "low_stock", label: "Low Stock", color: "secondary" };
    }
    return { status: "out_of_stock", label: "Out of Stock", color: "outline" };
  };

  const stockStatus = getStockStatus();

  // Auto-detect country from browser (client-side only)
  useEffect(() => {
    if (typeof window !== "undefined") {
      // Try to get country from localStorage or use default
      const savedCountry = localStorage.getItem("preferredCountry");
      if (savedCountry) {
        setCurrentCountry(savedCountry);
      }
    }
  }, []);

  if (!isAvailable && displayStock === 0) {
    return (
      <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg animate-fade-in">
        <AlertCircle className="h-5 w-5 text-red-600" />
        <div>
          <p className="font-semibold text-red-900">Out of Stock</p>
          <p className="text-sm text-red-700">
            This item is currently unavailable
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3 animate-fade-in">
      {/* Stock Status Badge */}
      <div className="flex items-center gap-3">
        <Badge variant={stockStatus.color as any} className="animate-scale-in">
          <div className="flex items-center gap-2">
            {stockStatus.status === "in_stock" && (
              <CheckCircle2 className="h-4 w-4" />
            )}
            {stockStatus.status === "low_stock" && (
              <AlertCircle className="h-4 w-4" />
            )}
            {stockStatus.status === "out_of_stock" && (
              <AlertCircle className="h-4 w-4" />
            )}
            <span>{stockStatus.label}</span>
          </div>
        </Badge>
        
        {displayStock !== null && displayStock !== undefined && (
          <span className="text-sm text-muted-foreground">
            {displayStock} {displayStock === 1 ? "item" : "items"} available
          </span>
        )}
      </div>

      {/* Country-Specific Stock */}
      {product.countrySpecificStock && Object.keys(product.countrySpecificStock).length > 0 && (
        <div className="border rounded-lg p-4 bg-secondary/50">
          <div className="flex items-center gap-2 mb-3">
            <MapPin className="h-4 w-4 text-muted-foreground" />
            <h4 className="text-sm font-semibold">Stock by Location</h4>
          </div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {Object.entries(product.countrySpecificStock).map(([country, stock]: [string, any]) => (
              <div
                key={country}
                className={`flex justify-between p-2 rounded ${
                  currentCountry === country ? "bg-primary/10 border border-primary/20" : ""
                }`}
              >
                <span className="text-muted-foreground">{country.toUpperCase()}:</span>
                <span className={`font-semibold ${
                  stock > 0 ? "text-green-600" : "text-red-600"
                }`}>
                  {stock > 0 ? `${stock} available` : "Out of stock"}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Stock Indicator */}
      {stockStatus.status === "low_stock" && (
        <div className="flex items-center gap-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800 animate-slide-in">
          <AlertCircle className="h-4 w-4" />
          <span>Only {displayStock} left in stock - order soon!</span>
        </div>
      )}
    </div>
  );
}

