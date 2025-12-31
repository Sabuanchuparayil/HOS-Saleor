import Link from "next/link";
import Image from "next/image";
import { Seller } from "@/types";
import { Badge } from "@/components/common/Badge";

interface SellerCardProps {
  seller: Seller | any;
}

export function SellerCard({ seller }: SellerCardProps) {
  const sellerTypeLabels: Record<string, string> = {
    b2b_wholesale: "B2B Wholesale",
    b2c_retail: "B2C Retail",
    hybrid: "B2B & B2C",
  };

  return (
    <Link href={`/sellers/${seller.slug}`} className="group">
      <div className="border rounded-lg p-6 hover:shadow-lg transition-shadow">
        <div className="flex items-center gap-4 mb-4">
          {seller.logo ? (
            <div className="relative w-16 h-16 rounded-full overflow-hidden bg-gray-100">
              <Image
                src={seller.logo.url}
                alt={seller.storeName}
                fill
                className="object-cover"
              />
            </div>
          ) : (
            <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center">
              <span className="text-2xl">🏪</span>
            </div>
          )}
          <div className="flex-1">
            <h3 className="font-semibold text-lg group-hover:text-primary transition-colors">
              {seller.storeName}
            </h3>
            {seller.sellerType && (
              <Badge variant="secondary" className="mt-1">
                {sellerTypeLabels[seller.sellerType] || seller.sellerType}
              </Badge>
            )}
          </div>
        </div>
        {seller.description && (
          <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
            {seller.description}
          </p>
        )}
        {seller.analytics && (
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>{seller.analytics.orderCount || 0} orders</span>
            {seller.analytics.revenue && (
              <span>
                {new Intl.NumberFormat("en-US", {
                  style: "currency",
                  currency: seller.analytics.revenue.currency,
                  notation: "compact",
                }).format(seller.analytics.revenue.amount)}
              </span>
            )}
          </div>
        )}
      </div>
    </Link>
  );
}

