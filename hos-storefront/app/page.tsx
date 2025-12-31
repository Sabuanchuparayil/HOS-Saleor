import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { HeroSection } from "@/components/common/HeroSection";
import { FeaturedProducts } from "@/components/product/FeaturedProducts";
import { FeaturedSellers } from "@/components/seller/FeaturedSellers";
import { FeaturedCollections } from "@/components/collection/FeaturedCollections";
import { NewsletterSignup } from "@/components/common/NewsletterSignup";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <HeroSection />
        <div className="container py-12 space-y-16">
          <FeaturedCollections />
          <FeaturedProducts />
          <FeaturedSellers />
          <NewsletterSignup />
        </div>
      </main>
      <Footer />
    </div>
  );
}
