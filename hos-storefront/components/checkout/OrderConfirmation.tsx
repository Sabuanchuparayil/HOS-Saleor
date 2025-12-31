"use client";

import { useQuery } from "@apollo/client/react";
import { GET_ORDER } from "@/lib/graphql/queries";
import { formatPrice, formatDate } from "@/lib/utils";
import { CheckCircle, Package, Mail } from "lucide-react";
import Link from "next/link";
import { Loader2 } from "lucide-react";

interface OrderConfirmationProps {
  orderId: string;
}

export function OrderConfirmation({ orderId }: OrderConfirmationProps) {
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

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 mb-4">
          <CheckCircle className="h-8 w-8 text-green-600" />
        </div>
        <h1 className="text-4xl font-bold mb-2">Order Confirmed!</h1>
        <p className="text-muted-foreground">
          Thank you for your purchase. Your order has been received.
        </p>
      </div>

      <div className="border rounded-lg p-6 mb-6">
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div>
            <p className="text-sm text-muted-foreground mb-1">Order Number</p>
            <p className="font-semibold">{order.number || order.id}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground mb-1">Order Date</p>
            <p className="font-semibold">
              {order.created ? formatDate(order.created) : "N/A"}
            </p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground mb-1">Status</p>
            <p className="font-semibold capitalize">{order.status || "Processing"}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground mb-1">Total</p>
            <p className="font-semibold">
              {order.total?.gross
                ? formatPrice(order.total.gross.amount / 100, order.total.gross.currency)
                : "N/A"}
            </p>
          </div>
        </div>

        {order.shippingAddress && (
          <div className="border-t pt-4">
            <div className="flex items-center gap-2 mb-3">
              <Package className="h-5 w-5" />
              <h3 className="font-semibold">Shipping Address</h3>
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
            </div>
          </div>
        )}
      </div>

      <div className="border rounded-lg p-6 mb-6">
        <h2 className="text-xl font-bold mb-4">Order Items</h2>
        <div className="space-y-4">
          {order.lines?.map((line: any) => {
            const product = line.variant?.product;
            const price = line.totalPrice?.gross;

            return (
              <div key={line.id} className="flex justify-between items-start">
                <div>
                  <p className="font-medium">{product?.name || "Product"}</p>
                  {line.variant && line.variant.name !== product?.name && (
                    <p className="text-sm text-muted-foreground">
                      Variant: {line.variant.name}
                    </p>
                  )}
                  <p className="text-sm text-muted-foreground">
                    Quantity: {line.quantity}
                  </p>
                </div>
                {price && (
                  <p className="font-semibold">
                    {formatPrice(price.amount / 100, price.currency)}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
          <Mail className="h-4 w-4" />
          <span>
            A confirmation email has been sent to your email address.
          </span>
        </div>
        <div className="flex gap-4 justify-center">
          <Link
            href="/products"
            className="px-6 py-3 border rounded-md font-semibold hover:bg-accent transition-colors"
          >
            Continue Shopping
          </Link>
          <Link
            href="/account/orders"
            className="px-6 py-3 bg-primary text-primary-foreground rounded-md font-semibold hover:bg-primary/90 transition-colors"
          >
            View Order History
          </Link>
        </div>
      </div>
    </div>
  );
}

