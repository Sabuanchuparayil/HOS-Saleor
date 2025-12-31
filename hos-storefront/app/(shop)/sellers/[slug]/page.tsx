import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { SellerStorefront } from "@/components/seller/SellerStorefront";

interface SellerPageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: SellerPageProps) {
  const { slug } = await params;
  return {
    title: `Seller Store | House of Spells`,
    description: "Browse products from this seller",
  };
}

export default async function SellerPage({ params }: SellerPageProps) {
  const { slug } = await params;

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container py-8">
        <SellerStorefront slug={slug} />
      </main>
      <Footer />
    </div>
  );
}

