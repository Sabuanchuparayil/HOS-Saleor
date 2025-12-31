import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { CheckoutPage } from "@/components/checkout/CheckoutPage";

export const metadata = {
  title: "Checkout",
  description: "Complete your purchase",
  robots: {
    index: false,
    follow: false,
  },
};

export default function Checkout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container py-8">
        <CheckoutPage />
      </main>
      <Footer />
    </div>
  );
}

