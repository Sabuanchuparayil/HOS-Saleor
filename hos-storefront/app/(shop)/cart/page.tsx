import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { CartPage } from "@/components/cart/CartPage";

export const metadata = {
  title: "Shopping Cart",
  description: "Review your cart items and proceed to checkout",
  openGraph: {
    title: "Shopping Cart | House of Spells",
    description: "Review your cart items and proceed to checkout",
  },
};

export default function Cart() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container py-8">
        <CartPage />
      </main>
      <Footer />
    </div>
  );
}

