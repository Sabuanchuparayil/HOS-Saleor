"use client";

import { useState } from "react";
import { useMutation } from "@apollo/client/react";
import { APPLY_DISCOUNT_CODE } from "@/lib/graphql/mutations";
import { Tag, X, Loader2 } from "lucide-react";

interface DiscountCodeProps {
  checkoutId: string;
  onDiscountApplied: () => void;
}

export function DiscountCode({ checkoutId, onDiscountApplied }: DiscountCodeProps) {
  const [code, setCode] = useState("");
  const [isApplying, setIsApplying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [appliedCode, setAppliedCode] = useState<string | null>(null);
  const [applyDiscount] = useMutation(APPLY_DISCOUNT_CODE);

  const handleApply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!code.trim()) return;

    setIsApplying(true);
    setError(null);

    try {
      const { data } = await applyDiscount({
        variables: {
          checkoutId,
          promoCode: code.trim(),
        },
      });

      const errors = (data as any)?.checkoutAddPromoCode?.errors;
      if (errors && errors.length > 0) {
        setError(errors[0].message);
      } else {
        setAppliedCode(code.trim());
        setCode("");
        onDiscountApplied();
      }
    } catch (err: any) {
      setError(err.message || "Failed to apply discount code");
    } finally {
      setIsApplying(false);
    }
  };

  const handleRemove = async () => {
    // In production, use checkoutRemovePromoCode mutation
    setAppliedCode(null);
    onDiscountApplied();
  };

  return (
    <div className="border rounded-lg p-4">
      <div className="flex items-center gap-2 mb-3">
        <Tag className="h-5 w-5 text-primary" />
        <h3 className="font-semibold">Discount Code</h3>
      </div>

      {appliedCode ? (
        <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-md">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-green-800">
              Code applied: {appliedCode}
            </span>
          </div>
          <button
            onClick={handleRemove}
            className="p-1 hover:bg-green-100 rounded transition-colors"
            aria-label="Remove discount code"
          >
            <X className="h-4 w-4 text-green-800" />
          </button>
        </div>
      ) : (
        <form onSubmit={handleApply} className="flex gap-2">
          <input
            type="text"
            value={code}
            onChange={(e) => {
              setCode(e.target.value);
              setError(null);
            }}
            placeholder="Enter discount code"
            className="flex-1 px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <button
            type="submit"
            disabled={isApplying || !code.trim()}
            className="px-6 py-2 bg-primary text-primary-foreground rounded-md font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isApplying ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              "Apply"
            )}
          </button>
        </form>
      )}

      {error && (
        <p className="mt-2 text-sm text-destructive">{error}</p>
      )}
    </div>
  );
}

