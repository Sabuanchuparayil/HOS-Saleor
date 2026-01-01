"use client";

import { formatPrice } from "@/lib/utils";
import { MapPin, CreditCard, Package } from "lucide-react";
import Image from "next/image";

interface OrderReviewProps {
  checkout: any;
  shippingAddress: any;
  paymentMethod: string | null;
  onComplete: () => void;
}

export function OrderReview({
  checkout,
  shippingAddress,
  paymentMethod,
  onComplete,
}: OrderReviewProps) {
  return (
    <div className="border rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-6">Review Your Order</h2>

      <div className="space-y-6">
        {/* Shipping Address */}
        {shippingAddress && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <MapPin className="h-5 w-5" />
              <h3 className="font-semibold">Shipping Address</h3>
            </div>
            <div className="pl-7 text-sm text-muted-foreground">
              <p>
                {shippingAddress.firstName} {shippingAddress.lastName}
              </p>
              <p>{shippingAddress.streetAddress1}</p>
              {shippingAddress.streetAddress2 && (
                <p>{shippingAddress.streetAddress2}</p>
              )}
              <p>
                {shippingAddress.city}, {shippingAddress.postalCode}
              </p>
              <p>{shippingAddress.country}</p>
              {shippingAddress.phone && <p>{shippingAddress.phone}</p>}
            </div>
          </div>
        )}

        {/* Payment Method */}
        {paymentMethod && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <CreditCard className="h-5 w-5" />
              <h3 className="font-semibold">Payment Method</h3>
            </div>
            <div className="pl-7 text-sm text-muted-foreground">
              <p className="capitalize">{paymentMethod}</p>
            </div>
          </div>
        )}

        {/* Order Items */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Package className="h-5 w-5" />
            <h3 className="font-semibold">Order Items</h3>
          </div>
          <div className="pl-7 space-y-3">
            {checkout.lines?.map((line: any) => {
              const product = line.variant?.product;
              const thumbnail = product?.thumbnail;
              const price = line.totalPrice?.gross;

              return (
                <div key={line.id} className="flex gap-4">
                  {thumbnail && (
                    <div className="relative w-16 h-16 rounded-lg overflow-hidden bg-gray-100 flex-shrink-0">
                      <Image
                        src={thumbnail.url}
                        alt={thumbnail.alt || product.name}
                        fill
                        className="object-cover"
                      />
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="font-medium">{product.name}</p>
                    {line.variant && line.variant.name !== product.name && (
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
                      {formatPrice(price.amount, price.currency)}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Order Summary */}
        <div className="border-t pt-6">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Subtotal</span>
              <span>
                {formatPrice(
                  checkout.subtotalPrice?.gross?.amount || 0,
                  checkout.subtotalPrice?.gross?.currency || "USD"
                )}
              </span>
            </div>
            {checkout.shippingPrice?.gross?.amount > 0 && (
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Shipping</span>
                <span>
                  {formatPrice(
                    checkout.shippingPrice.gross.amount,
                    checkout.shippingPrice.gross.currency
                  )}
                </span>
              </div>
            )}
            <div className="border-t pt-2 mt-2">
              <div className="flex justify-between font-bold text-lg">
                <span>Total</span>
                <span>
                  {formatPrice(
                    checkout.totalPrice?.gross?.amount || 0,
                    checkout.totalPrice?.gross?.currency || "USD"
                  )}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Complete Order Button */}
        <div className="flex gap-4 pt-4">
          <button
            type="button"
            onClick={() => window.history.back()}
            className="flex-1 px-6 py-3 border rounded-md font-semibold hover:bg-accent transition-colors"
          >
            Back
          </button>
          <button
            onClick={onComplete}
            className="flex-1 bg-primary text-primary-foreground px-6 py-3 rounded-md font-semibold hover:bg-primary/90 transition-colors"
          >
            Complete Order
          </button>
        </div>
      </div>
    </div>
  );
}


