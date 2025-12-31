import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { OrderConfirmation } from "@/components/checkout/OrderConfirmation";

interface OrderConfirmationPageProps {
  params: Promise<{ id: string }>;
}

export const metadata = {
  title: "Order Confirmation",
  description: "Your order has been placed successfully",
  robots: {
    index: false,
    follow: false,
  },
};

export default async function OrderConfirmationPage({
  params,
}: OrderConfirmationPageProps) {
  const { id } = await params;

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container py-8">
        <OrderConfirmation orderId={id} />
      </main>
      <Footer />
    </div>
  );
}

