import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { CollectionsListing } from "@/components/collection/CollectionsListing";

export const metadata = {
  title: "Collections",
  description: "Browse our product collections",
  openGraph: {
    title: "Collections | House of Spells",
    description: "Browse our product collections",
  },
};

export default function CollectionsPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container py-8">
        <CollectionsListing />
      </main>
      <Footer />
    </div>
  );
}

