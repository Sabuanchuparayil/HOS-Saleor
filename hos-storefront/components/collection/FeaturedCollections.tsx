"use client";

import { useQuery } from "@apollo/client/react";
import { ApolloError } from "@apollo/client";
import { GET_FEATURED_COLLECTIONS } from "@/lib/graphql/queries";
import Link from "next/link";
import Image from "next/image";
import { Loader2 } from "lucide-react";

export function FeaturedCollections() {
  const { data, loading, error } = useQuery(GET_FEATURED_COLLECTIONS, {
    variables: { first: 6 },
    errorPolicy: "all", // Continue even if there are errors
  });

  if (loading) {
    return (
      <section>
        <h2 className="text-3xl font-bold mb-8">Featured Collections</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-gray-200 aspect-video rounded-lg mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            </div>
          ))}
        </div>
      </section>
    );
  }

  if (error) {
    const apolloError = error as ApolloError;
    console.error("FeaturedCollections GraphQL Error:", error);
    console.error("Error details:", {
      message: error.message,
      graphQLErrors: apolloError.graphQLErrors,
      networkError: apolloError.networkError,
    });
    return null; // Silently fail for homepage
  }

  const collections = (data as any)?.featuredCollections?.edges?.map((edge: any) => edge.node) || [];

  if (collections.length === 0) {
    return null; // Don't show section if no collections
  }

  return (
    <section>
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-3xl font-bold">Featured Collections</h2>
        <Link
          href="/collections"
          className="text-primary hover:underline font-medium"
        >
          View All →
        </Link>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {collections.slice(0, 6).map((collection: any) => (
          <Link
            key={collection.id}
            href={`/collections/${collection.slug}`}
            className="group relative overflow-hidden rounded-lg border hover:shadow-lg transition-shadow"
          >
            {collection.backgroundImage ? (
              <div className="relative aspect-video">
                <Image
                  src={collection.backgroundImage.url}
                  alt={collection.backgroundImage.alt || collection.name}
                  fill
                  className="object-cover group-hover:scale-105 transition-transform"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
              </div>
            ) : (
              <div className="aspect-video bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center">
                <span className="text-4xl">📦</span>
              </div>
            )}
            <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
              <h3 className="text-xl font-bold mb-1">{collection.name}</h3>
              {collection.description && (
                <p className="text-sm text-white/90 line-clamp-2">
                  {collection.description}
                </p>
              )}
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}

