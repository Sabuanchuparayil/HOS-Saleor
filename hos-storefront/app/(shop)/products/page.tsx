import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { ProductListing } from "@/components/product/ProductListing";
import { Metadata } from "next";

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL || "https://hos-storefront-production.up.railway.app";

export const metadata: Metadata = {
  title: "All Products",
  description: "Browse all products from our marketplace sellers",
  openGraph: {
    title: "All Products | House of Spells",
    description: "Browse all products from our marketplace sellers",
  },
  alternates: {
    canonical: `${siteUrl}/products`,
  },
};

export default function ProductsPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">All Products</h1>
          <p className="text-muted-foreground">
            Discover magical products from authorized sellers worldwide
          </p>
        </div>
        <ProductListing />
      </main>
      <Footer />
    </div>
  );
}

