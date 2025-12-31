"use client";

import { formatPrice } from "@/lib/utils";
import Image from "next/image";
import { useMemo } from "react";

interface CheckoutSummaryProps {
  checkout: any;
}

export function CheckoutSummary({ checkout }: CheckoutSummaryProps) {
  const subtotal = checkout.subtotalPrice?.gross || { amount: 0, currency: "USD" };
  const shipping = checkout.shippingPrice?.gross || { amount: 0, currency: "USD" };
  const tax = checkout.totalPrice?.tax || { amount: 0, currency: "USD" };
  const total = checkout.totalPrice?.gross || { amount: 0, currency: "USD" };

  // Group items by seller for multi-seller split shipping display
  const itemsBySeller = useMemo(() => {
    if (!checkout.lines) return {};
    
    return checkout.lines.reduce((acc: any, line: any) => {
      const sellerId = line.variant?.product?.seller?.id || "no-seller";
      const sellerName = line.variant?.product?.seller?.storeName || "Unknown Seller";
      const sellerType = line.variant?.product?.seller?.sellerType || "b2c_retail";
      
      if (!acc[sellerId]) {
        acc[sellerId] = {
          seller: {
            id: sellerId,
            name: sellerName,
            type: sellerType,
          },
          items: [],
          subtotal: { amount: 0, currency: checkout.totalPrice?.gross?.currency || "USD" },
        };
      }
      
      acc[sellerId].items.push(line);
      const lineTotal = line.totalPrice?.gross?.amount || 0;
      acc[sellerId].subtotal.amount += lineTotal;
      
      return acc;
    }, {});
  }, [checkout.lines, checkout.totalPrice?.gross?.currency]);

  const sellerGroups = Object.values(itemsBySeller);
  const isMultiSeller = sellerGroups.length > 1;

  return (
    <div className="border rounded-lg p-6 bg-secondary/50 sticky top-8">
      <h2 className="text-xl font-bold mb-4">Order Summary</h2>

      {/* Order Items Preview */}
      <div className="space-y-3 mb-6 max-h-64 overflow-y-auto">
        {checkout.lines?.slice(0, 3).map((line: any) => {
          const product = line.variant?.product;
          const thumbnail = product?.thumbnail;

          return (
            <div key={line.id} className="flex gap-3">
              {thumbnail && (
                <div className="relative w-12 h-12 rounded-md overflow-hidden bg-gray-100 flex-shrink-0">
                  <Image
                    src={thumbnail.url}
                    alt={thumbnail.alt || product.name}
                    fill
                    className="object-cover"
                  />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium line-clamp-1">{product.name}</p>
                <p className="text-xs text-muted-foreground">
                  Qty: {line.quantity}
                </p>
              </div>
            </div>
          );
        })}
        {checkout.lines && checkout.lines.length > 3 && (
          <p className="text-xs text-muted-foreground text-center">
            +{checkout.lines.length - 3} more items
          </p>
        )}
      </div>

      {/* Multi-Seller Split Shipping Display */}
      {isMultiSeller && (
        <div className="mb-4 pb-4 border-b">
          <p className="text-xs text-muted-foreground mb-2">
            This order contains items from {sellerGroups.length} different sellers
          </p>
          <div className="space-y-2 text-xs">
            {sellerGroups.map((group: any) => (
              <div key={group.seller.id} className="flex justify-between">
                <span className="text-muted-foreground">
                  {group.seller.name} ({group.seller.type === "b2b_wholesale" ? "B2B" : "B2C"})
                </span>
                <span className="font-medium">
                  {formatPrice(group.subtotal.amount / 100, group.subtotal.currency)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Price Breakdown */}
      <div className="space-y-2 mb-4">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Subtotal</span>
          <span>{formatPrice(subtotal.amount / 100, subtotal.currency)}</span>
        </div>

        {shipping.amount > 0 && (
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">
              Shipping{isMultiSeller ? " (split by seller)" : ""}
            </span>
            <span>{formatPrice(shipping.amount / 100, shipping.currency)}</span>
          </div>
        )}

        {tax.amount > 0 && (
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Tax</span>
            <span>{formatPrice(tax.amount / 100, tax.currency)}</span>
          </div>
        )}
      </div>

      <div className="border-t pt-4">
        <div className="flex justify-between font-bold text-lg">
          <span>Total</span>
          <span>{formatPrice(total.amount / 100, total.currency)}</span>
        </div>
      </div>
    </div>
  );
}

