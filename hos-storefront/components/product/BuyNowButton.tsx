"use client";

import { useState } from "react";
import { useMutation } from "@apollo/client/react";
import { CREATE_CHECKOUT, ADD_TO_CART } from "@/lib/graphql/mutations";
import { Zap } from "lucide-react";
import { useRouter } from "next/navigation";

interface BuyNowButtonProps {
  variantId: string | null | undefined;
  quantity: number;
  productName: string;
}

export function BuyNowButton({
  variantId,
  quantity,
  productName,
}: BuyNowButtonProps) {
  const router = useRouter();
  const [isProcessing, setIsProcessing] = useState(false);
  const [createCheckout] = useMutation(CREATE_CHECKOUT);
  const [addToCart] = useMutation(ADD_TO_CART);

  const handleBuyNow = async () => {
    if (!variantId) {
      alert("Please select a variant");
      return;
    }

    setIsProcessing(true);

    try {
      // Create a new checkout with this single item
      const { data: checkoutData } = await createCheckout({
        variables: {
          lines: [{ variantId, quantity }],
        },
      });

      const checkoutId = (checkoutData as any)?.checkoutCreate?.checkout?.id;
      
      if (!checkoutId) {
        const errors = (checkoutData as any)?.checkoutCreate?.errors;
        if (errors && errors.length > 0) {
          alert(`Error: ${errors[0].message}`);
        } else {
          alert("Failed to create checkout. Please try again.");
        }
        setIsProcessing(false);
        return;
      }

      // Store checkout ID for checkout page
      localStorage.setItem("checkoutId", checkoutId);
      
      // Redirect directly to checkout
      router.push("/checkout");
    } catch (error: any) {
      console.error("Error in Buy Now:", error);
      alert("There was an error processing your request. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <button
      onClick={handleBuyNow}
      disabled={isProcessing || !variantId}
      className="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-6 py-3 rounded-md font-semibold hover:from-purple-700 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
    >
      <Zap className="h-5 w-5" />
      {isProcessing ? "Processing..." : "Buy Now"}
    </button>
  );
}

