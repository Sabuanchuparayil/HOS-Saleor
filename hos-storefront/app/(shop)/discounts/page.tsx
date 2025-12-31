import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { DiscountsListing } from "@/components/discount/DiscountsListing";
import { Metadata } from "next";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://hos-marketplaceweb-production.up.railway.app";

export const metadata: Metadata = {
  title: "Discounts & Promotions",
  description: "Browse all active discounts, promotions, and special offers from our sellers",
  openGraph: {
    title: "Discounts & Promotions | House of Spells",
    description: "Browse all active discounts, promotions, and special offers from our sellers",
  },
  alternates: {
    canonical: `${siteUrl}/discounts`,
  },
};

export default function DiscountsPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Discounts & Promotions</h1>
          <p className="text-muted-foreground">
            Discover amazing deals and special offers from our sellers
          </p>
        </div>
        <DiscountsListing />
      </main>
      <Footer />
    </div>
  );
}

