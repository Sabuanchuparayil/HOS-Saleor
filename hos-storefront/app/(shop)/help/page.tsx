import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Help Center",
  description: "Get help with your orders, account, and more",
};

export default function HelpPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 container py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold mb-8">Help Center</h1>
          
          <div className="space-y-8">
            <section>
              <h2 className="text-2xl font-semibold mb-4">Frequently Asked Questions</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-medium mb-2">How do I place an order?</h3>
                  <p className="text-muted-foreground">
                    Browse our products, add items to your cart, and proceed to checkout. 
                    You can checkout as a guest or create an account for faster future orders.
                  </p>
                </div>
                <div>
                  <h3 className="text-lg font-medium mb-2">How do I track my order?</h3>
                  <p className="text-muted-foreground">
                    Once your order is shipped, you'll receive a tracking number via email. 
                    You can also view your order status in your account dashboard.
                  </p>
                </div>
                <div>
                  <h3 className="text-lg font-medium mb-2">What is your return policy?</h3>
                  <p className="text-muted-foreground">
                    We accept returns within 30 days of delivery. Items must be unused and in original packaging. 
                    Visit the Returns page in your account to initiate a return.
                  </p>
                </div>
                <div>
                  <h3 className="text-lg font-medium mb-2">How do I contact customer support?</h3>
                  <p className="text-muted-foreground">
                    You can reach us through our Contact page or email us directly. 
                    Our support team typically responds within 24 hours.
                  </p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">Account Help</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-medium mb-2">How do I create an account?</h3>
                  <p className="text-muted-foreground">
                    You can create an account during checkout or by visiting the Account page. 
                    Having an account allows you to track orders, save addresses, and manage preferences.
                  </p>
                </div>
                <div>
                  <h3 className="text-lg font-medium mb-2">I forgot my password</h3>
                  <p className="text-muted-foreground">
                    Use the "Forgot Password" link on the login page to reset your password. 
                    You'll receive an email with instructions.
                  </p>
                </div>
              </div>
            </section>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}

