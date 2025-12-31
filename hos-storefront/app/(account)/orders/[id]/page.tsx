import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { OrderDetails } from "@/components/account/OrderDetails";

interface OrderDetailsPageProps {
  params: Promise<{ id: string }>;
}

export const metadata = {
  title: "Order Details",
  robots: {
    index: false,
    follow: false,
  },
};

export default async function OrderDetailsPage({
  params,
}: OrderDetailsPageProps) {
  const { id } = await params;

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container py-8">
        <OrderDetails orderId={id} />
      </main>
      <Footer />
    </div>
  );
}

