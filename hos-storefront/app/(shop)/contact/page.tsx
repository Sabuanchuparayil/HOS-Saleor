import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Contact Us",
  description: "Get in touch with House of Spells customer support",
};

export default function ContactPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container py-8">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-4xl font-bold mb-8">Contact Us</h1>
          
          <div className="space-y-8">
            <section>
              <h2 className="text-2xl font-semibold mb-4">Get in Touch</h2>
              <p className="text-muted-foreground mb-6">
                Have a question or need assistance? We're here to help! 
                Reach out to us through any of the methods below.
              </p>
              
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-medium mb-2">Email Support</h3>
                  <p className="text-muted-foreground">
                    <a href="mailto:support@houseofspells.com" className="text-primary hover:underline">
                      support@houseofspells.com
                    </a>
                  </p>
                  <p className="text-sm text-muted-foreground mt-1">
                    We typically respond within 24 hours
                  </p>
                </div>
                
                <div>
                  <h3 className="text-lg font-medium mb-2">Business Hours</h3>
                  <p className="text-muted-foreground">
                    Monday - Friday: 9:00 AM - 6:00 PM GMT<br />
                    Saturday: 10:00 AM - 4:00 PM GMT<br />
                    Sunday: Closed
                  </p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">Common Inquiries</h2>
              <div className="space-y-3 text-muted-foreground">
                <p><strong>Order Issues:</strong> Include your order number for faster assistance</p>
                <p><strong>Product Questions:</strong> We can help you find the right product</p>
                <p><strong>Seller Inquiries:</strong> For seller-related questions, visit our Sellers page</p>
                <p><strong>Technical Support:</strong> Report any website issues you encounter</p>
              </div>
            </section>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}

