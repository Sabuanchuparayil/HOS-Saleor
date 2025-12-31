import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { ReturnsManagement } from "@/components/account/ReturnsManagement";

export const metadata = {
  title: "Returns",
  description: "Manage your return requests",
  robots: {
    index: false,
    follow: false,
  },
};

export default function ReturnsPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container py-8">
        <ReturnsManagement />
      </main>
      <Footer />
    </div>
  );
}

