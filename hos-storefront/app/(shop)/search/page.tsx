import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { SearchResults } from "@/components/search/SearchResults";

interface SearchPageProps {
  searchParams: Promise<{ q?: string }>;
}

export async function generateMetadata({ searchParams }: SearchPageProps) {
  const { q } = await searchParams;
  return {
    title: q ? `Search: ${q} | House of Spells` : "Search | House of Spells",
    description: q
      ? `Search results for "${q}"`
      : "Search for products and sellers",
  };
}

export default async function SearchPage({ searchParams }: SearchPageProps) {
  const { q } = await searchParams;
  const query = q || "";

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container py-8">
        <SearchResults query={query} />
      </main>
      <Footer />
    </div>
  );
}

