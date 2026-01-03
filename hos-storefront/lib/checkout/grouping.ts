export type CheckoutLineGroup = {
  /** Stable grouping key. Prefers seller.id, falls back to product.id/variant.id. */
  id: string;
  /** Display label (seller name when available, otherwise product name). */
  name: string;
  /** Seller type when available; otherwise "unknown". */
  type: string;
  /** How the grouping was computed. */
  mode: "seller" | "product" | "unknown";
};

export function getCheckoutLineGroup(line: any): CheckoutLineGroup {
  const product = line?.variant?.product;
  const seller = product?.seller;

  if (seller?.id) {
    return {
      id: seller.id,
      name: seller.storeName || "Seller",
      type: seller.sellerType || "unknown",
      mode: "seller",
    };
  }

  const productId = product?.id || line?.variant?.id || line?.id || "unknown";
  const productName = product?.name || "Item";

  return {
    id: `product:${productId}`,
    name: productName,
    type: "unknown",
    mode: product?.id ? "product" : "unknown",
  };
}


