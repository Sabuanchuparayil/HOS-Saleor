"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation } from "@apollo/client/react";
import { GET_CHECKOUT } from "@/lib/graphql/queries";
import {
  CHECKOUT_PAYMENT_CREATE,
  COMPLETE_CHECKOUT,
  CREATE_CHECKOUT,
} from "@/lib/graphql/mutations";
import { ShippingAddress } from "./ShippingAddress";
import { PaymentMethod } from "./PaymentMethod";
import { OrderReview } from "./OrderReview";
import { CheckoutSummary } from "./CheckoutSummary";
import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";

type CheckoutStep = "shipping" | "payment" | "review";

export function CheckoutPage() {
  const router = useRouter();
  const [checkoutId, setCheckoutId] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<CheckoutStep>("shipping");
  const [shippingAddress, setShippingAddress] = useState<any>(null);
  const [paymentMethod, setPaymentMethod] = useState<{ gateway: string; token: string } | null>(
    null
  );
  const [multiCheckout, setMultiCheckout] = useState<any>(null);
  const [multiIndex, setMultiIndex] = useState<number>(0);

  useEffect(() => {
    const storedMulti = localStorage.getItem("multiCheckout");
    if (storedMulti) {
      try {
        const parsed = JSON.parse(storedMulti);
        if (parsed?.checkouts?.length) {
          const idx = typeof parsed.currentIndex === "number" ? parsed.currentIndex : 0;
          setMultiCheckout(parsed);
          setMultiIndex(idx);
          setCheckoutId(parsed.checkouts[idx]?.checkoutId || null);
          return;
        }
      } catch {
        // ignore
      }
    }

    const storedCheckoutId = localStorage.getItem("checkoutId");
    if (storedCheckoutId) {
      setCheckoutId(storedCheckoutId);
    } else {
      // Create new checkout if none exists
      createNewCheckout();
    }
  }, []);

  const [createCheckout] = useMutation(CREATE_CHECKOUT);
  const [createPayment] = useMutation(CHECKOUT_PAYMENT_CREATE);
  const [completeCheckout, { loading: completing }] = useMutation(COMPLETE_CHECKOUT);

  const createNewCheckout = async () => {
    try {
      const { data } = await createCheckout({
        variables: {
          email: null,
          channel: process.env.NEXT_PUBLIC_SALEOR_CHANNEL || null,
          lines: [],
        },
      });
      const newCheckoutId = (data as any)?.checkoutCreate?.checkout?.id;
      if (newCheckoutId) {
        setCheckoutId(newCheckoutId);
        localStorage.setItem("checkoutId", newCheckoutId);
      }
    } catch (error) {
      console.error("Error creating checkout:", error);
    }
  };

  const { data, loading, error, refetch } = useQuery(GET_CHECKOUT, {
    variables: { id: checkoutId },
    skip: !checkoutId,
  });

  const checkout = (data as any)?.checkout;

  const handleShippingSubmit = (address: any) => {
    setShippingAddress(address);
    setCurrentStep("payment");
  };

  const handlePaymentSubmit = (payment: { gateway: string; token: string }) => {
    setPaymentMethod(payment);
    setCurrentStep("review");
  };

  const handleCompleteOrder = async () => {
    if (!checkoutId) return;

    try {
      const checkout = (data as any)?.checkout;
      const amount = checkout?.totalPrice?.gross?.amount;
      const currency = checkout?.totalPrice?.gross?.currency;

      if (!paymentMethod) {
        alert("Please select a payment method.");
        return;
      }
      if (typeof amount !== "number" || !currency) {
        alert("Checkout total is missing. Please refresh and try again.");
        return;
      }

      // 1) Create payment with gateway + token (Stripe test token supported)
      const paymentRes = await createPayment({
        variables: {
          checkoutId,
          input: {
            gateway: paymentMethod.gateway,
            token: paymentMethod.token,
            amount,
          },
        },
      });

      const paymentErrors = (paymentRes.data as any)?.checkoutPaymentCreate?.errors || [];
      if (paymentErrors.length) {
        alert(
          paymentErrors.map((e: any) => e.message).filter(Boolean).join("\n") ||
            "Failed to create payment."
        );
        return;
      }

      // 2) Complete checkout (creates order)
      const { data: completeData } = await completeCheckout({
        variables: {
          checkoutId,
        },
      });

      const completeErrors = (completeData as any)?.checkoutComplete?.errors || [];
      if (completeErrors.length) {
        alert(
          completeErrors.map((e: any) => e.message).filter(Boolean).join("\n") ||
            "Failed to complete checkout."
        );
        return;
      }

      const order = (completeData as any)?.checkoutComplete?.order;
      if (order) {
        // Multi-checkout flow: progress to next seller checkout
        const storedMulti = localStorage.getItem("multiCheckout");
        if (storedMulti) {
          const parsed = JSON.parse(storedMulti);
          const nextOrders = Array.isArray(parsed.orders) ? [...parsed.orders, order.id] : [order.id];
          const nextIndex = (parsed.currentIndex ?? 0) + 1;

          if (nextIndex < (parsed.checkouts?.length || 0)) {
            parsed.orders = nextOrders;
            parsed.currentIndex = nextIndex;
            localStorage.setItem("multiCheckout", JSON.stringify(parsed));

            // Reset step state for next seller
            setShippingAddress(null);
            setPaymentMethod(null);
            setCurrentStep("shipping");
            setMultiCheckout(parsed);
            setMultiIndex(nextIndex);
            setCheckoutId(parsed.checkouts[nextIndex]?.checkoutId || null);
            return;
          }

          // Finished all seller checkouts
          localStorage.removeItem("multiCheckout");
          router.push("/account/orders");
          return;
        }

        // Single-checkout flow
        localStorage.removeItem("checkoutId");
        router.push(`/order-confirmation/${order.id}`);
      }
    } catch (error) {
      console.error("Error completing checkout:", error);
      alert("There was an error processing your order. Please try again.");
    }
  };

  if (loading || !checkoutId) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive mb-4">Error loading checkout</p>
        <p className="text-sm text-muted-foreground">{error.message}</p>
      </div>
    );
  }

  if (!checkout || !checkout.lines || checkout.lines.length === 0) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold mb-2">Your cart is empty</h2>
        <p className="text-muted-foreground mb-6">
          Add items to your cart before checkout
        </p>
        <a
          href="/products"
          className="inline-flex items-center justify-center rounded-lg bg-primary px-6 py-3 text-primary-foreground font-semibold hover:bg-primary/90 transition-colors"
        >
          Continue Shopping
        </a>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-4xl font-bold">Checkout</h1>
        {multiCheckout?.checkouts?.length > 1 && (
          <p className="text-sm text-muted-foreground mt-2">
            Seller checkout {multiIndex + 1} of {multiCheckout.checkouts.length}:{" "}
            <span className="font-medium text-foreground">
              {multiCheckout.checkouts[multiIndex]?.sellerName || "Seller"}
            </span>
          </p>
        )}
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {["shipping", "payment", "review"].map((step, index) => {
            const stepLabel = step.charAt(0).toUpperCase() + step.slice(1);
            const isActive = currentStep === step;
            const isCompleted =
              (step === "shipping" && currentStep !== "shipping") ||
              (step === "payment" && currentStep === "review");

            return (
              <div key={step} className="flex items-center flex-1">
                <div className="flex flex-col items-center">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                      isActive || isCompleted
                        ? "bg-primary text-primary-foreground"
                        : "bg-secondary text-secondary-foreground"
                    }`}
                  >
                    {isCompleted ? "✓" : index + 1}
                  </div>
                  <span
                    className={`mt-2 text-sm ${
                      isActive ? "font-semibold text-primary" : "text-muted-foreground"
                    }`}
                  >
                    {stepLabel}
                  </span>
                </div>
                {index < 2 && (
                  <div
                    className={`flex-1 h-1 mx-4 ${
                      isCompleted ? "bg-primary" : "bg-secondary"
                    }`}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          {currentStep === "shipping" && (
            <ShippingAddress
              checkout={checkout}
              onSubmit={handleShippingSubmit}
              refetchCheckout={refetch}
            />
          )}
          {currentStep === "payment" && (
            <PaymentMethod
              checkout={checkout}
              onSubmit={handlePaymentSubmit}
            />
          )}
          {currentStep === "review" && (
            <OrderReview
              checkout={checkout}
              shippingAddress={shippingAddress}
              paymentMethod={paymentMethod?.gateway || null}
              onComplete={handleCompleteOrder}
            />
          )}
        </div>

        <div className="lg:col-span-1">
          <CheckoutSummary checkout={checkout} />
        </div>
      </div>
    </div>
  );
}

