"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation } from "@apollo/client/react";
import { GET_CHECKOUT } from "@/lib/graphql/queries";
import { UPDATE_CHECKOUT_LINES, DELETE_CHECKOUT_LINES } from "@/lib/graphql/mutations";
import { CartItem } from "./CartItem";
import { CartSummary } from "./CartSummary";
import { DiscountCode } from "./DiscountCode";
import { Loader2, ShoppingBag } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getCheckoutLineGroup } from "@/lib/checkout/grouping";

export function CartPage() {
  const router = useRouter();
  const [checkoutId, setCheckoutId] = useState<string | null>(null);

  // Get checkout ID from localStorage or create new one
  useEffect(() => {
    const storedCheckoutId = localStorage.getItem("checkoutId");
    if (storedCheckoutId) {
      setCheckoutId(storedCheckoutId);
    }
  }, []);

  const { data, loading, error, refetch } = useQuery(GET_CHECKOUT, {
    variables: { id: checkoutId },
    skip: !checkoutId,
  });

  const [updateLines] = useMutation(UPDATE_CHECKOUT_LINES);
  const [deleteLines] = useMutation(DELETE_CHECKOUT_LINES);

  const checkout = (data as any)?.checkout;

  const handleUpdateQuantity = async (lineId: string, quantity: number) => {
    if (!checkoutId) return;

    try {
      await updateLines({
        variables: {
          checkoutId,
          lines: [{ lineId, quantity }],
        },
      });
      refetch();
    } catch (error) {
      console.error("Error updating quantity:", error);
    }
  };

  const handleRemoveItem = async (lineId: string) => {
    if (!checkoutId) return;

    try {
      await deleteLines({
        variables: {
          checkoutId,
          lines: [lineId],
        },
      });
      refetch();
    } catch (error) {
      console.error("Error removing item:", error);
    }
  };

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
        <p className="text-destructive mb-4">Error loading cart</p>
        <p className="text-sm text-muted-foreground">{error.message}</p>
      </div>
    );
  }

  if (!checkout || !checkout.lines || checkout.lines.length === 0) {
    return (
      <div className="text-center py-12">
        <ShoppingBag className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
        <h2 className="text-2xl font-bold mb-2">Your cart is empty</h2>
        <p className="text-muted-foreground mb-6">
          Start shopping to add items to your cart
        </p>
        <Link
          href="/products"
          className="inline-flex items-center justify-center rounded-lg bg-primary px-6 py-3 text-primary-foreground font-semibold hover:bg-primary/90 transition-colors"
        >
          Continue Shopping
        </Link>
      </div>
    );
  }

  // Group items by seller for multi-seller order splitting
  const itemsBySeller = checkout.lines.reduce((acc: any, line: any) => {
    const group = getCheckoutLineGroup(line);
    const sellerId = group.id;
    const sellerName = group.mode === "seller" ? group.name : `${group.name} (grouped)`;
    
    if (!acc[sellerId]) {
      acc[sellerId] = {
        seller: {
          id: sellerId,
          name: sellerName,
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

  const sellerGroups = Object.values(itemsBySeller);

  return (
    <div>
      <h1 className="text-4xl font-bold mb-8">Shopping Cart</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          {checkoutId && (
            <DiscountCode checkoutId={checkoutId} onDiscountApplied={refetch} />
          )}
          {sellerGroups.map((group: any, index: number) => (
            <div key={group.seller.id} className="border rounded-lg p-6">
              <div className="flex items-center gap-2 mb-4 pb-4 border-b">
                <h2 className="font-semibold text-lg">Seller: {group.seller.name}</h2>
                {index < sellerGroups.length - 1 && (
                  <span className="text-xs text-muted-foreground">
                    (Separate order)
                  </span>
                )}
              </div>
              <div className="space-y-4">
                {group.items.map((line: any) => (
                  <CartItem
                    key={line.id}
                    line={line}
                    onUpdateQuantity={handleUpdateQuantity}
                    onRemove={handleRemoveItem}
                  />
                ))}
              </div>
              <div className="mt-4 pt-4 border-t flex justify-end">
                <p className="text-sm text-muted-foreground">
                  Subtotal:{" "}
                  <span className="font-semibold text-foreground">
                    {new Intl.NumberFormat("en-US", {
                      style: "currency",
                      currency: group.subtotal.currency,
                    }).format(group.subtotal.amount)}
                  </span>
                </p>
              </div>
            </div>
          ))}
        </div>

        <div className="lg:col-span-1">
          <CartSummary checkout={checkout} />
        </div>
      </div>
    </div>
  );
}

