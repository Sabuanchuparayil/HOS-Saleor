import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { CollectionDetail } from "@/components/collection/CollectionDetail";

interface CollectionPageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: CollectionPageProps) {
  const { slug } = await params;
  return {
    title: `Collection | House of Spells`,
    description: "Browse products in this collection",
  };
}

export default async function CollectionPage({ params }: CollectionPageProps) {
  const { slug } = await params;

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container py-8">
        <CollectionDetail slug={slug} />
      </main>
      <Footer />
    </div>
  );
}

