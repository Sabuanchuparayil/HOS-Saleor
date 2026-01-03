"use client";

import { useState } from "react";
import { loadStripe } from "@stripe/stripe-js";
import { CardElement, Elements, useElements, useStripe } from "@stripe/react-stripe-js";
import { Loader2 } from "lucide-react";

const publishableKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;
const stripePromise = publishableKey ? loadStripe(publishableKey) : null;

function InnerStripeElementsPayment({
  onToken,
}: {
  onToken: (paymentMethodId: string) => void;
}) {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreatePaymentMethod = async () => {
    setError(null);
    if (!stripe || !elements) return;

    const card = elements.getElement(CardElement);
    if (!card) return;

    setLoading(true);
    try {
      const { error, paymentMethod } = await stripe.createPaymentMethod({
        type: "card",
        card,
      });

      if (error) {
        setError(error.message || "Failed to tokenize card.");
        return;
      }

      if (!paymentMethod?.id) {
        setError("Stripe did not return a payment method id.");
        return;
      }

      onToken(paymentMethod.id);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4 p-4 border rounded-lg bg-secondary/50">
      <div>
        <label className="block text-sm font-medium mb-2">
          Card Details <span className="text-destructive">*</span>
        </label>
        <div className="px-4 py-3 border rounded-md bg-background">
          <CardElement
            options={{
              hidePostalCode: true,
              style: {
                base: { fontSize: "16px" },
              },
            }}
          />
        </div>
        {error && <p className="text-sm text-destructive mt-2">{error}</p>}
      </div>

      <button
        type="button"
        onClick={handleCreatePaymentMethod}
        disabled={!stripe || !elements || loading}
        className="w-full inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-primary-foreground font-semibold hover:bg-primary/90 disabled:opacity-50"
      >
        {loading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin mr-2" />
            Tokenizing…
          </>
        ) : (
          "Use this card"
        )}
      </button>
    </div>
  );
}

export function StripeElementsPayment({
  onToken,
}: {
  onToken: (paymentMethodId: string) => void;
}) {
  if (!stripePromise) return null;

  return (
    <Elements stripe={stripePromise}>
      <InnerStripeElementsPayment onToken={onToken} />
    </Elements>
  );
}


