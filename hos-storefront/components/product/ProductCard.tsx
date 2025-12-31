import Link from "next/link";
import Image from "next/image";
import { formatPrice } from "@/lib/utils";
import { Product } from "@/types";

interface ProductCardProps {
  product: Product;
}

export function ProductCard({ product }: ProductCardProps) {
  const price = product.defaultVariant?.pricing?.price?.gross;
  const thumbnail = product.thumbnail;

  return (
    <Link href={`/products/${product.slug}`} className="group animate-fade-in">
      <div className="relative aspect-square overflow-hidden rounded-lg bg-gray-100 mb-4 transition-smooth group-hover:shadow-lg">
        {thumbnail ? (
          <Image
            src={thumbnail.url}
            alt={thumbnail.alt || product.name}
            fill
            className="object-cover transition-transform duration-500 group-hover:scale-110"
            loading="lazy"
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">
            No Image
          </div>
        )}
        {/* Overlay on hover */}
        <div className="absolute inset-0 bg-primary/0 group-hover:bg-primary/5 transition-colors duration-300" />
      </div>
      <div className="transition-smooth">
        <h3 className="font-semibold mb-1 line-clamp-2 group-hover:text-primary transition-colors duration-300">
          {product.name}
        </h3>
        {product.seller && (
          <p className="text-sm text-muted-foreground mb-2 group-hover:text-foreground transition-colors duration-300">
            by {product.seller.storeName}
          </p>
        )}
        {price && (
          <p className="text-lg font-bold transition-transform duration-300 group-hover:scale-105">
            {formatPrice(price.amount, price.currency)}
          </p>
        )}
      </div>
    </Link>
  );
}

