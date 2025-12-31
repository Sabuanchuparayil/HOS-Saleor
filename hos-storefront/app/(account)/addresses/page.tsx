import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { AddressBook } from "@/components/account/AddressBook";

export const metadata = {
  title: "Address Book",
  description: "Manage your shipping addresses",
  robots: {
    index: false,
    follow: false,
  },
};

export default function AddressesPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container py-8">
        <AddressBook />
      </main>
      <Footer />
    </div>
  );
}

