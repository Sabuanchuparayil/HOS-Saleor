"use client";

import { useState } from "react";
import { CreditCard, Lock, KeyRound } from "lucide-react";
import { StripeElementsPayment } from "./StripeElementsPayment";

interface PaymentMethodProps {
  checkout: any;
  onSubmit: (payment: { gateway: string; token: string }) => void;
}

export function PaymentMethod({ checkout, onSubmit }: PaymentMethodProps) {
  const stripeGatewayId =
    process.env.NEXT_PUBLIC_STRIPE_GATEWAY_ID || "saleor.payments.stripe";
  const stripePublishableKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;

  const [selectedMethod, setSelectedMethod] = useState<string>(
    process.env.NEXT_PUBLIC_PAYMENT_GATEWAY || stripeGatewayId
  );
  const [token, setToken] = useState<string>(
    process.env.NEXT_PUBLIC_STRIPE_TEST_TOKEN || "tok_visa"
  );

  const paymentMethods = [
    { id: stripeGatewayId, name: "Credit/Debit Card (Stripe)", icon: CreditCard },
    // Add more payment methods as needed
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In production, tokenize via Stripe Elements or a Saleor payment app.
    onSubmit({ gateway: selectedMethod, token });
  };

  return (
    <div className="border rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-6">Payment Method</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-3">
          {paymentMethods.map((method) => {
            const Icon = method.icon;
            return (
              <label
                key={method.id}
                className={`flex items-center gap-3 p-4 border rounded-lg cursor-pointer transition-colors ${
                  selectedMethod === method.id
                    ? "border-primary bg-primary/5"
                    : "hover:bg-accent"
                }`}
              >
                <input
                  type="radio"
                  name="paymentMethod"
                  value={method.id}
                  checked={selectedMethod === method.id}
                  onChange={(e) => setSelectedMethod(e.target.value)}
                  className="w-4 h-4"
                />
                <Icon className="h-5 w-5" />
                <span className="font-medium">{method.name}</span>
              </label>
            );
          })}
        </div>

        {selectedMethod === stripeGatewayId && stripePublishableKey ? (
          <StripeElementsPayment
            onToken={(paymentMethodId) => {
              setToken(paymentMethodId);
            }}
          />
        ) : (
          <div className="space-y-4 p-4 border rounded-lg bg-secondary/50">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <KeyRound className="h-4 w-4" />
              <span>
                Token mode: enter a gateway token (e.g. Stripe test token{" "}
                <code>tok_visa</code>).
              </span>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Payment Token <span className="text-destructive">*</span>
              </label>
              <input
                type="text"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="tok_visa"
                className="w-full px-4 py-2 border rounded-md"
              />
              <p className="text-xs text-muted-foreground mt-2">
                To enable Stripe Elements, set{" "}
                <code>NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY</code> in Railway.
              </p>
            </div>
          </div>
        )}

        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Lock className="h-4 w-4" />
          <span>Your payment information is secure and encrypted</span>
        </div>

        <div className="flex gap-4">
          <button
            type="button"
            onClick={() => window.history.back()}
            className="flex-1 px-6 py-3 border rounded-md font-semibold hover:bg-accent transition-colors"
          >
            Back
          </button>
          <button
            type="submit"
            className="flex-1 bg-primary text-primary-foreground px-6 py-3 rounded-md font-semibold hover:bg-primary/90 transition-colors"
          >
            Continue to Review
          </button>
        </div>
      </form>
    </div>
  );
}


