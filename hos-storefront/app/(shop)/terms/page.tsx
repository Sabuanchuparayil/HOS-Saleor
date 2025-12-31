import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms of Service",
  description: "House of Spells Terms of Service",
};

export default function TermsPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold mb-8">Terms of Service</h1>
          
          <div className="prose prose-slate max-w-none space-y-6">
            <section>
              <h2 className="text-2xl font-semibold mb-4">Last Updated: {new Date().toLocaleDateString()}</h2>
              <p className="text-muted-foreground">
                Please read these Terms of Service carefully before using the House of Spells marketplace.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">Acceptance of Terms</h2>
              <p className="text-muted-foreground">
                By accessing and using this website, you accept and agree to be bound by the terms 
                and provision of this agreement.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">Use License</h2>
              <p className="text-muted-foreground mb-4">
                Permission is granted to temporarily access the materials on House of Spells' website 
                for personal, non-commercial transitory viewing only.
              </p>
              <p className="text-muted-foreground">
                This license does not include:
              </p>
              <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                <li>Modifying or copying the materials</li>
                <li>Using the materials for commercial purposes</li>
                <li>Removing any copyright or proprietary notations</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">Orders and Payment</h2>
              <p className="text-muted-foreground mb-4">
                When you place an order, you agree to:
              </p>
              <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                <li>Provide accurate and complete information</li>
                <li>Pay all charges incurred by your account</li>
                <li>Accept delivery of products ordered</li>
                <li>Comply with all applicable laws and regulations</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">Returns and Refunds</h2>
              <p className="text-muted-foreground">
                Returns are accepted within 30 days of delivery, subject to our Return Policy. 
                Refunds will be processed to the original payment method within 5-10 business days 
                after we receive and inspect the returned item.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">Seller Responsibilities</h2>
              <p className="text-muted-foreground">
                Sellers on our marketplace are responsible for the accuracy of their product listings, 
                fulfillment of orders, and customer service. House of Spells acts as a platform 
                connecting buyers and sellers.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">Limitation of Liability</h2>
              <p className="text-muted-foreground">
                House of Spells shall not be liable for any indirect, incidental, special, 
                consequential, or punitive damages resulting from your use of the service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">Contact Information</h2>
              <p className="text-muted-foreground">
                For questions about these Terms, please contact us at{" "}
                <a href="mailto:legal@houseofspells.com" className="text-primary hover:underline">
                  legal@houseofspells.com
                </a>
              </p>
            </section>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}

