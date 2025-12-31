import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { SellerListing } from "@/components/seller/SellerListing";

export const metadata = {
  title: "All Sellers",
  description: "Browse all sellers in our marketplace",
  openGraph: {
    title: "All Sellers | House of Spells",
    description: "Browse all sellers in our marketplace",
  },
};

export default function SellersPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">All Sellers</h1>
          <p className="text-muted-foreground">
            Discover authorized sellers offering magical products
          </p>
        </div>
        <SellerListing />
      </main>
      <Footer />
    </div>
  );
}

