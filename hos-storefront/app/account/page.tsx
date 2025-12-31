import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { AccountDashboard } from "@/components/account/AccountDashboard";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "My Account",
  description: "Manage your account, orders, and preferences",
  robots: {
    index: false,
    follow: false,
  },
};

export default function AccountPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container py-8">
        <AccountDashboard />
      </main>
      <Footer />
    </div>
  );
}

