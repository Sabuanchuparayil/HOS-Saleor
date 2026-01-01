"use client";

import { formatPrice } from "@/lib/utils";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface CartSummaryProps {
  checkout: any;
}

export function CartSummary({ checkout }: CartSummaryProps) {
  const router = useRouter();

  const subtotal = checkout.subtotalPrice?.gross || { amount: 0, currency: "USD" };
  const shipping = checkout.shippingPrice?.gross || { amount: 0, currency: "USD" };
  const tax = checkout.totalPrice?.tax || { amount: 0, currency: "USD" };
  const total = checkout.totalPrice?.gross || { amount: 0, currency: "USD" };
  const discount = checkout.discount?.amount || 0;

  const handleCheckout = () => {
    router.push("/checkout");
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
        className="w-full bg-primary text-primary-foreground px-6 py-3 rounded-md font-semibold hover:bg-primary/90 transition-colors mb-4"
      >
        Proceed to Checkout
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


