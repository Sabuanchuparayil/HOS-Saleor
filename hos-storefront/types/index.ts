// Product Types
export interface Product {
  id: string;
  name: string;
  slug: string;
  description?: string;
  seoTitle?: string;
  seoDescription?: string;
  rating?: number;
  reviewCount?: number;
  defaultVariant?: ProductVariant;
  thumbnail?: Image;
  seller?: Seller;
  approvalStatus?: string;
  rrp?: Money;
  variants?: ProductVariant[];
  images?: Image[];
  collections?: Collection[];
}

export interface ProductVariant {
  id: string;
  name: string;
  sku?: string;
  pricing?: {
    price?: {
      gross?: Money;
      net?: Money;
    };
  };
}

export interface Image {
  url: string;
  alt?: string;
}

export interface Money {
  amount: number;
  currency: string;
}

// Seller Types
export interface Seller {
  id: string;
  storeName: string;
  slug: string;
  description?: string;
  logo?: Image;
  sellerType?: "b2b_wholesale" | "b2c_retail" | "hybrid";
  status?: string;
  analytics?: SellerAnalytics;
}

export interface SellerAnalytics {
  revenue?: Money;
  earnings?: Money;
  orderCount?: number;
  platformFeeTotal?: Money;
}

// Collection Types
export interface Collection {
  id: string;
  name: string;
  slug: string;
  description?: string;
  backgroundImage?: Image;
}

// Cart Types
export interface CartItem {
  id: string;
  quantity: number;
  variant: ProductVariant;
  product: Product;
}

export interface Cart {
  id: string;
  items: CartItem[];
  totalPrice: Money;
}


