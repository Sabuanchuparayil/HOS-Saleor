import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { ProductDetail } from "@/components/product/ProductDetail";
import { notFound } from "next/navigation";
import { Metadata } from "next";
import { ApolloClient, InMemoryCache, createHttpLink } from "@apollo/client";
import { GET_PRODUCT_BY_SLUG } from "@/lib/graphql/queries";

interface ProductPageProps {
  params: Promise<{ slug: string }>;
}

// ISR: Revalidate every 60 seconds
export const revalidate = 60;

export async function generateStaticParams() {
  // In production, fetch popular products for static generation
  // For now, return empty array to use dynamic rendering
  return [];
}

export async function generateMetadata({ params }: ProductPageProps): Promise<Metadata> {
  const { slug } = await params;
  
  try {
    // Create a server-side Apollo client for metadata generation
    const httpLink = createHttpLink({
      uri: process.env.NEXT_PUBLIC_SALEOR_API_URL || "https://hos-saleor-production.up.railway.app/graphql/",
    });

    const client = new ApolloClient({
      link: httpLink,
      cache: new InMemoryCache(),
      ssrMode: true,
    });

    const { data } = await client.query<{
      products?: {
        edges?: Array<{
          node?: {
            id: string;
            name: string;
            slug: string;
            description?: string;
            seoTitle?: string;
            seoDescription?: string;
            thumbnail?: { url: string; alt?: string };
          };
        }>;
      };
    }>({
      query: GET_PRODUCT_BY_SLUG,
      variables: { slug },
      context: { fetchOptions: { next: { revalidate: 60 } } },
    });

    const product = data?.products?.edges?.[0]?.node;
    
    if (!product) {
      return {
        title: "Product Not Found | House of Spells",
        description: "The requested product could not be found",
      };
    }

    return {
      title: product.seoTitle || `${product.name} | House of Spells`,
      description: product.seoDescription || product.description || "Product details and information",
      openGraph: {
        title: product.name,
        description: product.description || product.seoDescription,
        images: product.thumbnail ? [{ url: product.thumbnail.url }] : [],
        type: "website",
      },
      twitter: {
        card: "summary_large_image",
        title: product.name,
        description: product.description || product.seoDescription,
        images: product.thumbnail ? [product.thumbnail.url] : [],
      },
    };
  } catch (error) {
    return {
      title: "Product | House of Spells",
      description: "Product details and information",
    };
  }
}

export default async function ProductPage({ params }: ProductPageProps) {
  const { slug } = await params;
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://hos-marketplaceweb-production.up.railway.app";
  const canonicalUrl = `${siteUrl}/products/${slug}`;

  return (
    <>
      <link rel="canonical" href={canonicalUrl} />
      <div className="flex min-h-screen flex-col">
        <Header />
        <main className="flex-1 container py-8">
          <ProductDetail slug={slug} />
        </main>
        <Footer />
      </div>
    </>
  );
}

