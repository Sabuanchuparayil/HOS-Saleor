"use client";

import { formatPrice } from "@/lib/utils";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation } from "@apollo/client/react";
import { CREATE_CHECKOUT, DELETE_CHECKOUT_LINES } from "@/lib/graphql/mutations";
import { useMemo, useState } from "react";
import { getCheckoutLineGroup } from "@/lib/checkout/grouping";

interface CartSummaryProps {
  checkout: any;
}

export function CartSummary({ checkout }: CartSummaryProps) {
  const router = useRouter();
  const [isSplitting, setIsSplitting] = useState(false);
  const [createCheckout] = useMutation(CREATE_CHECKOUT);
  const [deleteLines] = useMutation(DELETE_CHECKOUT_LINES);

  const subtotal = checkout.subtotalPrice?.gross || { amount: 0, currency: "USD" };
  const shipping = checkout.shippingPrice?.gross || { amount: 0, currency: "USD" };
  const tax = checkout.totalPrice?.tax || { amount: 0, currency: "USD" };
  const total = checkout.totalPrice?.gross || { amount: 0, currency: "USD" };
  const discount = checkout.discount?.amount || 0;

  const sellerGroups = useMemo(() => {
    const lines: any[] = checkout?.lines || [];
    const groups = new Map<string, { sellerId: string; sellerName: string; lines: any[] }>();
    for (const line of lines) {
      const group = getCheckoutLineGroup(line);
      const sellerId = group.id;
      const sellerName = group.mode === "seller" ? group.name : `${group.name} (grouped)`;
      const existing = groups.get(sellerId);
      if (existing) existing.lines.push(line);
      else groups.set(sellerId, { sellerId, sellerName, lines: [line] });
    }
    return Array.from(groups.values());
  }, [checkout]);

  const handleCheckout = async () => {
    const hasMultipleSellers = sellerGroups.length > 1;
    if (!hasMultipleSellers) {
      router.push("/checkout");
      return;
    }

    // Option A: create one checkout per seller (split shipping)
    setIsSplitting(true);
    try {
      const channel = checkout?.channel?.slug || process.env.NEXT_PUBLIC_SALEOR_CHANNEL || null;
      const email = checkout?.email || null;

      const created: Array<{
        sellerId: string;
        sellerName: string;
        checkoutId: string;
        token: string;
      }> = [];

      for (const group of sellerGroups) {
        const linesInput = group.lines.map((line: any) => ({
          variantId: line.variant.id,
          quantity: line.quantity,
        }));

        const { data } = await createCheckout({
          variables: {
            email,
            channel,
            lines: linesInput,
          },
        });

        const newCheckout = (data as any)?.checkoutCreate?.checkout;
        if (!newCheckout?.id) {
          throw new Error("Failed to create seller checkout");
        }

        created.push({
          sellerId: group.sellerId,
          sellerName: group.sellerName,
          checkoutId: newCheckout.id,
          token: newCheckout.token,
        });
      }

      // Clear the original cart checkout lines to avoid double-order risk
      const lineIds = (checkout?.lines || []).map((l: any) => l.id);
      if (lineIds.length) {
        await deleteLines({
          variables: {
            checkoutId: checkout.id,
            lines: lineIds,
          },
        });
      }

      // Store multi-checkout plan for /checkout
      const payload = {
        createdAt: Date.now(),
        originalCheckoutId: checkout.id,
        checkouts: created,
        currentIndex: 0,
        orders: [] as string[],
      };
      localStorage.setItem("multiCheckout", JSON.stringify(payload));
      localStorage.removeItem("checkoutId");

      router.push("/checkout");
    } catch (e: any) {
      console.error(e);
      alert(
        "Could not split your cart into separate seller checkouts. Please try again."
      );
    } finally {
      setIsSplitting(false);
    }
  };

  return (
    <div className="border rounded-lg p-6 bg-secondary/50 sticky top-8">
      <h2 className="text-xl font-bold mb-4">Order Summary</h2>
      
      <div className="space-y-3 mb-4">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Subtotal</span>
          <span>{formatPrice(subtotal.amount, subtotal.currency)}</span>
        </div>
        
        {shipping.amount > 0 && (
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Shipping</span>
            <span>{formatPrice(shipping.amount, shipping.currency)}</span>
          </div>
        )}
        
        {tax.amount > 0 && (
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Tax</span>
            <span>{formatPrice(tax.amount, tax.currency)}</span>
          </div>
        )}
        
        {discount > 0 && (
          <div className="flex justify-between text-sm text-green-600">
            <span>Discount</span>
            <span>-{formatPrice(discount, subtotal.currency)}</span>
          </div>
        )}
      </div>
      
      <div className="border-t pt-4 mb-6">
        <div className="flex justify-between font-bold text-lg">
          <span>Total</span>
          <span>{formatPrice(total.amount, total.currency)}</span>
        </div>
      </div>
      
      <button
        onClick={handleCheckout}
        disabled={isSplitting}
        className="w-full bg-primary text-primary-foreground px-6 py-3 rounded-md font-semibold hover:bg-primary/90 transition-colors mb-4"
      >
        {isSplitting ? "Preparing seller checkouts..." : "Proceed to Checkout"}
      </button>
      
      <Link
        href="/products"
        className="block text-center text-sm text-primary hover:underline"
      >
        Continue Shopping
      </Link>
    </div>
  );
}


