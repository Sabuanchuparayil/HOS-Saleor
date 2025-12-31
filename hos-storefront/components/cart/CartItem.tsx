"use client";

import Image from "next/image";
import Link from "next/link";
import { formatPrice } from "@/lib/utils";
import { Minus, Plus, Trash2 } from "lucide-react";
import { useState } from "react";

interface CartItemProps {
  line: any;
  onUpdateQuantity: (lineId: string, quantity: number) => void;
  onRemove: (lineId: string) => void;
}

export function CartItem({ line, onUpdateQuantity, onRemove }: CartItemProps) {
  const [quantity, setQuantity] = useState(line.quantity);
  const [isUpdating, setIsUpdating] = useState(false);

  const product = line.variant?.product;
  const variant = line.variant;
  const price = line.totalPrice?.gross;
  const thumbnail = product?.thumbnail;

  const handleQuantityChange = async (newQuantity: number) => {
    if (newQuantity < 1) return;
    
    setIsUpdating(true);
    setQuantity(newQuantity);
    await onUpdateQuantity(line.id, newQuantity);
    setIsUpdating(false);
  };

  const handleRemove = async () => {
    if (confirm("Are you sure you want to remove this item?")) {
      await onRemove(line.id);
    }
  };

  return (
    <div className="flex gap-4">
      {thumbnail && (
        <Link href={`/products/${product.slug}`} className="flex-shrink-0">
          <div className="relative w-24 h-24 rounded-lg overflow-hidden bg-gray-100">
            <Image
              src={thumbnail.url}
              alt={thumbnail.alt || product.name}
              fill
              className="object-cover"
            />
          </div>
        </Link>
      )}
      
      <div className="flex-1 min-w-0">
        <Link href={`/products/${product.slug}`}>
          <h3 className="font-semibold hover:text-primary transition-colors mb-1">
            {product.name}
          </h3>
        </Link>
        {variant && variant.name !== product.name && (
          <p className="text-sm text-muted-foreground mb-2">Variant: {variant.name}</p>
        )}
        {product.seller && (
          <p className="text-xs text-muted-foreground mb-2">
            by {product.seller.storeName}
          </p>
        )}
        
        <div className="flex items-center justify-between mt-4">
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleQuantityChange(quantity - 1)}
              disabled={isUpdating || quantity <= 1}
              className="p-1 rounded-md border hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Minus className="h-4 w-4" />
            </button>
            <span className="w-12 text-center font-medium">{quantity}</span>
            <button
              onClick={() => handleQuantityChange(quantity + 1)}
              disabled={isUpdating}
              className="p-1 rounded-md border hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Plus className="h-4 w-4" />
            </button>
          </div>
          
          <div className="flex items-center gap-4">
            {price && (
              <p className="font-semibold">
                {formatPrice(price.amount / 100, price.currency)}
              </p>
            )}
            <button
              onClick={handleRemove}
              className="p-2 text-destructive hover:bg-destructive/10 rounded-md transition-colors"
              aria-label="Remove item"
            >
              <Trash2 className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

