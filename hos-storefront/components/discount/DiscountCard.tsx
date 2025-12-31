"use client";

import { useState, useEffect } from "react";
import { Tag, Clock, Copy, CheckCircle2 } from "lucide-react";
import { Badge } from "@/components/common/Badge";
import Link from "next/link";
import { formatPrice } from "@/lib/utils";

interface DiscountCardProps {
  discount: any;
}

export function DiscountCard({ discount }: DiscountCardProps) {
  const [timeRemaining, setTimeRemaining] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // Calculate time remaining for countdown
  useEffect(() => {
    if (discount.endDate) {
      const updateCountdown = () => {
        const now = new Date();
        const end = new Date(discount.endDate);
        const diff = end.getTime() - now.getTime();

        if (diff <= 0) {
          setTimeRemaining("Expired");
          return;
        }

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

        if (days > 0) {
          setTimeRemaining(`${days}d ${hours}h`);
        } else if (hours > 0) {
          setTimeRemaining(`${hours}h ${minutes}m`);
        } else {
          setTimeRemaining(`${minutes}m`);
        }
      };

      updateCountdown();
      const interval = setInterval(updateCountdown, 60000); // Update every minute

      return () => clearInterval(interval);
    }
  }, [discount.endDate]);

  const handleCopyCode = () => {
    if (discount.type === "voucher" && discount.code) {
      navigator.clipboard.writeText(discount.code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getDiscountValue = () => {
    if (discount.type === "promotion") {
      const rule = discount.rules?.[0];
      if (rule?.rewardValueType === "PERCENTAGE") {
        return `${rule.rewardValue}% OFF`;
      } else if (rule?.rewardValueType === "FIXED") {
        return `$${rule.rewardValue} OFF`;
      }
    } else if (discount.type === "voucher") {
      if (discount.discountValueType === "PERCENTAGE") {
        return `${discount.discountValue}% OFF`;
      } else if (discount.discountValueType === "FIXED") {
        return `$${discount.discountValue} OFF`;
      }
    }
    return "Special Offer";
  };

  return (
    <div className="border rounded-lg p-6 hover:shadow-lg transition-all duration-300 bg-gradient-to-br from-primary/5 to-primary/10 animate-scale-in">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2">
          <Tag className="h-5 w-5 text-primary" />
          <Badge variant="default" className="animate-pulse-glow">
            {getDiscountValue()}
          </Badge>
        </div>
        {discount.type === "voucher" && discount.code && (
          <button
            onClick={handleCopyCode}
            className="p-2 hover:bg-primary/10 rounded transition-colors"
            title="Copy code"
          >
            {copied ? (
              <CheckCircle2 className="h-4 w-4 text-green-600" />
            ) : (
              <Copy className="h-4 w-4 text-muted-foreground" />
            )}
          </button>
        )}
      </div>

      <h3 className="font-bold text-lg mb-2">{discount.name}</h3>
      
      {discount.description && (
        <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
          {discount.description}
        </p>
      )}

      {/* Voucher Code Display */}
      {discount.type === "voucher" && discount.code && (
        <div className="mb-4 p-3 bg-background border-2 border-dashed border-primary/30 rounded-lg">
          <p className="text-xs text-muted-foreground mb-1">Voucher Code</p>
          <p className="font-mono font-bold text-lg text-primary">{discount.code}</p>
        </div>
      )}

      {/* Time Remaining Countdown */}
      {discount.endDate && timeRemaining && (
        <div className="flex items-center gap-2 mb-4 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm">
          <Clock className="h-4 w-4 text-yellow-600" />
          <span className="text-yellow-800 font-medium">
            {timeRemaining === "Expired" ? "Expired" : `Ends in ${timeRemaining}`}
          </span>
        </div>
      )}

      {/* Seller Info */}
      {discount.seller && (
        <div className="mb-4">
          <p className="text-xs text-muted-foreground mb-1">From</p>
          <Link
            href={`/sellers/${discount.seller.slug}`}
            className="text-sm font-semibold text-primary hover:underline transition-colors"
          >
            {discount.seller.storeName}
          </Link>
        </div>
      )}

      {/* CTA Button */}
      <Link
        href={discount.type === "voucher" ? "/cart" : "/products"}
        className="block w-full text-center bg-primary text-primary-foreground px-4 py-2 rounded-md font-semibold hover:bg-primary/90 transition-all duration-300 hover:scale-105"
      >
        {discount.type === "voucher" ? "Use in Cart" : "Shop Now"}
      </Link>
    </div>
  );
}

