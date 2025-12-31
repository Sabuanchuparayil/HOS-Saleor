"use client";

import { useQuery } from "@apollo/client/react";
import { GET_ORDER } from "@/lib/graphql/queries";
import { formatPrice, formatDate } from "@/lib/utils";
import { MapPin, Package, CreditCard, Loader2 } from "lucide-react";
import Link from "next/link";
import Image from "next/image";

interface OrderDetailsProps {
  orderId: string;
}

export function OrderDetails({ orderId }: OrderDetailsProps) {
  const { data, loading, error } = useQuery(GET_ORDER, {
    variables: { id: orderId },
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
        <p className="text-destructive mb-4">Error loading order</p>
        <p className="text-sm text-muted-foreground">{error.message}</p>
      </div>
    );
  }

  const order = (data as any)?.order;
  if (!order) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Order not found</p>
      </div>
    );
  }

  // Group items by seller for multi-seller order breakdown
  const itemsBySeller = order.lines?.reduce((acc: any, line: any) => {
    // Use denormalized seller info if available, fallback to product seller
    const sellerId = line.seller?.id || line.variant?.product?.seller?.id || "no-seller";
    const sellerName = line.sellerName || line.seller?.storeName || line.variant?.product?.seller?.storeName || "Unknown Seller";
    
    if (!acc[sellerId]) {
      acc[sellerId] = {
        seller: {
          id: sellerId,
          name: sellerName,
        },
        items: [],
        subtotal: { amount: 0, currency: order.total?.gross?.currency || "USD" },
      };
    }
    
    acc[sellerId].items.push(line);
    const lineTotal = line.totalPrice?.gross?.amount || 0;
    acc[sellerId].subtotal.amount += lineTotal;
    
    return acc;
  }, {});

  const sellerGroups = Object.values(itemsBySeller || {});

  return (
    <div>
      <div className="mb-8">
        <Link
          href="/account/orders"
          className="text-primary hover:underline mb-4 inline-block"
        >
          ← Back to Orders
        </Link>
        <h1 className="text-4xl font-bold mb-2">
          Order #{order.number || order.id.slice(-8)}
        </h1>
        <p className="text-muted-foreground">
          Placed on {formatDate(order.created)}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          {/* Order Items by Seller */}
          {sellerGroups.map((group: any, index: number) => (
            <div key={group.seller.id} className="border rounded-lg p-6">
              <div className="flex items-center gap-2 mb-4 pb-4 border-b">
                <Package className="h-5 w-5" />
                <h2 className="font-semibold text-lg">Seller: {group.seller.name}</h2>
                {index < sellerGroups.length - 1 && (
                  <span className="text-xs text-muted-foreground ml-2">
                    (Separate shipment)
                  </span>
                )}
              </div>
              <div className="space-y-4">
                {group.items.map((line: any) => {
                  const product = line.variant?.product;
                  const thumbnail = product?.thumbnail;
                  const price = line.totalPrice?.gross;

                  return (
                    <div key={line.id} className="flex gap-4">
                      {thumbnail && (
                        <Link href={`/products/${product.slug}`} className="flex-shrink-0">
                          <div className="relative w-20 h-20 rounded-lg overflow-hidden bg-gray-100">
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
                        {line.variant && line.variant.name !== product.name && (
                          <p className="text-sm text-muted-foreground mb-1">
                            Variant: {line.variant.name}
                          </p>
                        )}
                        <p className="text-sm text-muted-foreground">
                          Quantity: {line.quantity}
                        </p>
                      </div>
                      {price && (
                        <div className="text-right">
                          <p className="font-semibold">
                            {formatPrice(price.amount / 100, price.currency)}
                          </p>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
              <div className="mt-4 pt-4 border-t flex justify-end">
                <p className="text-sm text-muted-foreground">
                  Subtotal:{" "}
                  <span className="font-semibold text-foreground">
                    {formatPrice(
                      group.subtotal.amount / 100,
                      group.subtotal.currency
                    )}
                  </span>
                </p>
              </div>
            </div>
          ))}

          {/* Shipping Address */}
          {order.shippingAddress && (
            <div className="border rounded-lg p-6">
              <div className="flex items-center gap-2 mb-4">
                <MapPin className="h-5 w-5" />
                <h2 className="font-semibold text-lg">Shipping Address</h2>
              </div>
              <div className="text-sm text-muted-foreground">
                <p>
                  {order.shippingAddress.firstName} {order.shippingAddress.lastName}
                </p>
                <p>{order.shippingAddress.streetAddress1}</p>
                {order.shippingAddress.streetAddress2 && (
                  <p>{order.shippingAddress.streetAddress2}</p>
                )}
                <p>
                  {order.shippingAddress.city}, {order.shippingAddress.postalCode}
                </p>
                <p>{order.shippingAddress.country?.code}</p>
                {order.shippingAddress.phone && <p>{order.shippingAddress.phone}</p>}
              </div>
            </div>
          )}
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <div className="border rounded-lg p-6 bg-secondary/50 sticky top-8">
            <h2 className="text-xl font-bold mb-4">Order Summary</h2>
            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Subtotal</span>
                <span>
                  {order.subtotal?.gross
                    ? formatPrice(
                        order.subtotal.gross.amount / 100,
                        order.subtotal.gross.currency
                      )
                    : "N/A"}
                </span>
              </div>
              {order.shippingPrice?.gross?.amount > 0 && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Shipping</span>
                  <span>
                    {formatPrice(
                      order.shippingPrice.gross.amount / 100,
                      order.shippingPrice.gross.currency
                    )}
                  </span>
                </div>
              )}
              {order.total?.tax?.amount > 0 && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Tax</span>
                  <span>
                    {formatPrice(
                      order.total.tax.amount / 100,
                      order.total.tax.currency
                    )}
                  </span>
                </div>
              )}
            </div>
            <div className="border-t pt-4 mb-4">
              <div className="flex justify-between font-bold text-lg">
                <span>Total</span>
                <span>
                  {order.total?.gross
                    ? formatPrice(
                        order.total.gross.amount / 100,
                        order.total.gross.currency
                      )
                    : "N/A"}
                </span>
              </div>
            </div>
            <div className="pt-4 border-t">
              <p className="text-sm text-muted-foreground mb-2">Status</p>
              <span
                className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                  order.status === "FULFILLED"
                    ? "bg-green-100 text-green-800"
                    : order.status === "UNFULFILLED"
                    ? "bg-yellow-100 text-yellow-800"
                    : order.status === "CANCELED"
                    ? "bg-red-100 text-red-800"
                    : "bg-gray-100 text-gray-800"
                }`}
              >
                {order.status || "Processing"}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

