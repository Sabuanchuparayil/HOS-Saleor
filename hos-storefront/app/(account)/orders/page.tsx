import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { OrderHistory } from "@/components/account/OrderHistory";

export const metadata = {
  title: "Order History",
  description: "View your order history",
  robots: {
    index: false,
    follow: false,
  },
};

export default function OrdersPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container py-8">
        <OrderHistory />
      </main>
      <Footer />
    </div>
  );
}

