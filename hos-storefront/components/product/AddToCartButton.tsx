"use client";

import { useState } from "react";
import { useMutation } from "@apollo/client/react";
import { ADD_TO_CART } from "@/lib/graphql/mutations";
import { ShoppingCart } from "lucide-react";
import { useRouter } from "next/navigation";

interface AddToCartButtonProps {
  variantId: string | null | undefined;
  quantity: number;
  productName: string;
}

export function AddToCartButton({
  variantId,
  quantity,
  productName,
}: AddToCartButtonProps) {
  const router = useRouter();
  const [isAdding, setIsAdding] = useState(false);
  const [addToCart] = useMutation(ADD_TO_CART);

  const handleAddToCart = async () => {
    if (!variantId) {
      alert("Please select a variant");
      return;
    }

    setIsAdding(true);

    try {
      // Get or create checkout
      let checkoutId = localStorage.getItem("checkoutId");
      
      if (!checkoutId) {
        // Create new checkout - in production, use CREATE_CHECKOUT mutation
        // For now, we'll show a message
        alert("Please add items to cart from the product listing page first");
        setIsAdding(false);
        return;
      }

      const { data } = await addToCart({
        variables: {
          checkoutId,
          variantId,
          quantity,
        },
      });

      const errors = (data as any)?.checkoutLinesAdd?.errors;
      if (errors && errors.length > 0) {
        alert(`Error: ${errors[0].message}`);
      } else {
        // Show success message or redirect to cart
        router.push("/cart");
      }
    } catch (error: any) {
      console.error("Error adding to cart:", error);
      alert("There was an error adding the item to your cart. Please try again.");
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <button
      onClick={handleAddToCart}
      disabled={isAdding || !variantId}
      className="flex-1 flex items-center justify-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded-md font-semibold hover:bg-primary/90 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95 hover:scale-105 hover:shadow-lg"
    >
      <ShoppingCart className={`h-5 w-5 transition-transform duration-300 ${isAdding ? 'animate-spin' : 'group-hover:scale-110'}`} />
      {isAdding ? "Adding..." : "Add to Cart"}
    </button>
  );
}

