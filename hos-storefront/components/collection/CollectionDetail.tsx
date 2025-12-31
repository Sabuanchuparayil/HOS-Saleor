"use client";

import { useQuery } from "@apollo/client/react";
import { GET_COLLECTION } from "@/lib/graphql/queries";
import { ProductCard } from "@/components/product/ProductCard";
import Image from "next/image";
import { Loader2 } from "lucide-react";
import Link from "next/link";

interface CollectionDetailProps {
  slug: string;
}

export function CollectionDetail({ slug }: CollectionDetailProps) {
  const { data, loading, error } = useQuery(GET_COLLECTION, {
    variables: { slug },
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
        <p className="text-destructive mb-4">Error loading collection</p>
        <p className="text-sm text-muted-foreground">{error.message}</p>
      </div>
    );
  }

  const collection = (data as any)?.collection;
  if (!collection) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Collection not found</p>
      </div>
    );
  }

  const products = collection.products?.edges?.map((edge: any) => edge.node) || [];

  return (
    <div>
      <Link
        href="/collections"
        className="text-primary hover:underline mb-4 inline-block"
      >
        ← Back to Collections
      </Link>

      {collection.backgroundImage && (
        <div className="relative h-64 md:h-96 rounded-lg overflow-hidden mb-8">
          <Image
            src={collection.backgroundImage.url}
            alt={collection.backgroundImage.alt || collection.name}
            fill
            className="object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          <div className="absolute bottom-0 left-0 right-0 p-8 text-white">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">{collection.name}</h1>
            {collection.description && (
              <p className="text-lg text-white/90 max-w-2xl">
                {collection.description}
              </p>
            )}
          </div>
        </div>
      )}

      {!collection.backgroundImage && (
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-4">{collection.name}</h1>
          {collection.description && (
            <p className="text-lg text-muted-foreground max-w-2xl">
              {collection.description}
            </p>
          )}
        </div>
      )}

      <div>
        <h2 className="text-2xl font-bold mb-6">
          Products ({products.length})
        </h2>
        {products.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {products.map((product: any) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No products in this collection</p>
          </div>
        )}
      </div>
    </div>
  );
}

