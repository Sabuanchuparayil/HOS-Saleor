"use client";

import { useQuery } from "@apollo/client/react";
import { GET_FEATURED_COLLECTIONS } from "@/lib/graphql/queries";
import Link from "next/link";
import Image from "next/image";
import { Loader2 } from "lucide-react";

export function CollectionsListing() {
  const { data, loading, error } = useQuery(GET_FEATURED_COLLECTIONS, {
    variables: { first: 50 },
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive mb-4">Error loading collections</p>
        <p className="text-sm text-muted-foreground">{error.message}</p>
      </div>
    );
  }

  const collections = (data as any)?.featuredCollections?.edges?.map((edge: any) => edge.node) || [];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Collections</h1>
        <p className="text-muted-foreground">
          Browse products by collection
        </p>
      </div>

      {collections.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {collections.map((collection: any) => (
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
                <h3 className="text-2xl font-bold mb-2">{collection.name}</h3>
                {collection.description && (
                  <p className="text-sm text-white/90 line-clamp-2">
                    {collection.description}
                  </p>
                )}
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No collections available</p>
        </div>
      )}
    </div>
  );
}

