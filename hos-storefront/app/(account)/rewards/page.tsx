import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { RewardsPage } from "@/components/account/RewardsPage";

export const metadata = {
  title: "Loyalty & Rewards",
  description: "View points, rewards, and recent loyalty activity",
  robots: {
    index: false,
    follow: false,
  },
};

export default function Rewards() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container py-8">
        <RewardsPage />
      </main>
      <Footer />
    </div>
  );
}


