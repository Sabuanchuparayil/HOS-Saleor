"use client";

import { useState } from "react";
import { useQuery } from "@apollo/client/react";
import { GET_PROMOTIONS, GET_VOUCHERS } from "@/lib/graphql/queries";
import { DiscountCard } from "./DiscountCard";
import { Loader2, Tag, Sparkles } from "lucide-react";
import { Badge } from "@/components/common/Badge";

export function DiscountsListing() {
  const [activeTab, setActiveTab] = useState<"all" | "promotions" | "vouchers">("all");

  const { data: promotionsData, loading: promotionsLoading } = useQuery(GET_PROMOTIONS, {
    variables: { first: 50 },
  });

  const { data: vouchersData, loading: vouchersLoading } = useQuery(GET_VOUCHERS, {
    variables: { first: 50 },
  });

  const promotions = (promotionsData as any)?.promotions?.edges?.map((edge: any) => edge.node) || [];
  const vouchers = (vouchersData as any)?.vouchers?.edges?.map((edge: any) => edge.node) || [];

  // Filter active promotions/vouchers
  const activePromotions = promotions.filter((p: any) => {
    const now = new Date();
    const startDate = p.startDate ? new Date(p.startDate) : null;
    const endDate = p.endDate ? new Date(p.endDate) : null;
    return (!startDate || startDate <= now) && (!endDate || endDate >= now);
  });

  const activeVouchers = vouchers.filter((v: any) => {
    const now = new Date();
    const startDate = v.startDate ? new Date(v.startDate) : null;
    const endDate = v.endDate ? new Date(v.endDate) : null;
    return v.isActive && (!startDate || startDate <= now) && (!endDate || endDate >= now);
  });

  const loading = promotionsLoading || vouchersLoading;

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  const allDiscounts = [
    ...activePromotions.map((p: any) => ({ ...p, type: "promotion" })),
    ...activeVouchers.map((v: any) => ({ ...v, type: "voucher" })),
  ];

  return (
    <div>
      {/* Header with tabs */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="h-6 w-6 text-primary" />
          <h2 className="text-2xl font-bold">Active Offers</h2>
        </div>
        <div className="flex gap-2 border-b">
          <button
            onClick={() => setActiveTab("all")}
            className={`px-4 py-2 font-medium transition-all duration-300 ${
              activeTab === "all"
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            All ({allDiscounts.length})
          </button>
          <button
            onClick={() => setActiveTab("promotions")}
            className={`px-4 py-2 font-medium transition-all duration-300 ${
              activeTab === "promotions"
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Promotions ({activePromotions.length})
          </button>
          <button
            onClick={() => setActiveTab("vouchers")}
            className={`px-4 py-2 font-medium transition-all duration-300 ${
              activeTab === "vouchers"
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Vouchers ({activeVouchers.length})
          </button>
        </div>
      </div>

      {/* Discounts Grid */}
      {((activeTab === "all" && allDiscounts.length > 0) ||
        (activeTab === "promotions" && activePromotions.length > 0) ||
        (activeTab === "vouchers" && activeVouchers.length > 0)) ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {(activeTab === "all"
            ? allDiscounts
            : activeTab === "promotions"
            ? activePromotions.map((p: any) => ({ ...p, type: "promotion" }))
            : activeVouchers.map((v: any) => ({ ...v, type: "voucher" }))
          ).map((discount: any, index: number) => (
            <div
              key={discount.id}
              className="animate-fade-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <DiscountCard discount={discount} />
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 border rounded-lg">
          <Tag className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground mb-2">No active discounts at the moment</p>
          <p className="text-sm text-muted-foreground">
            Check back soon for new promotions and offers!
          </p>
        </div>
      )}
    </div>
  );
}

