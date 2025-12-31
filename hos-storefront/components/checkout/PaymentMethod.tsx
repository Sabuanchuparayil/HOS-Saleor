"use client";

import { useState } from "react";
import { CreditCard, Lock } from "lucide-react";

interface PaymentMethodProps {
  checkout: any;
  onSubmit: (method: string) => void;
}

export function PaymentMethod({ checkout, onSubmit }: PaymentMethodProps) {
  const [selectedMethod, setSelectedMethod] = useState<string>("stripe");
  const [cardDetails, setCardDetails] = useState({
    number: "",
    expiry: "",
    cvv: "",
    name: "",
  });

  const paymentMethods = [
    { id: "stripe", name: "Credit/Debit Card", icon: CreditCard },
    // Add more payment methods as needed
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In production, validate and tokenize card details
    onSubmit(selectedMethod);
  };

  return (
    <div className="border rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-6">Payment Method</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-3">
          {paymentMethods.map((method) => {
            const Icon = method.icon;
            return (
              <label
                key={method.id}
                className={`flex items-center gap-3 p-4 border rounded-lg cursor-pointer transition-colors ${
                  selectedMethod === method.id
                    ? "border-primary bg-primary/5"
                    : "hover:bg-accent"
                }`}
              >
                <input
                  type="radio"
                  name="paymentMethod"
                  value={method.id}
                  checked={selectedMethod === method.id}
                  onChange={(e) => setSelectedMethod(e.target.value)}
                  className="w-4 h-4"
                />
                <Icon className="h-5 w-5" />
                <span className="font-medium">{method.name}</span>
              </label>
            );
          })}
        </div>

        {selectedMethod === "stripe" && (
          <div className="space-y-4 p-4 border rounded-lg bg-secondary/50">
            <div>
              <label className="block text-sm font-medium mb-1">
                Card Number <span className="text-destructive">*</span>
              </label>
              <input
                type="text"
                value={cardDetails.number}
                onChange={(e) =>
                  setCardDetails({ ...cardDetails, number: e.target.value })
                }
                placeholder="1234 5678 9012 3456"
                className="w-full px-4 py-2 border rounded-md"
                maxLength={19}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  Expiry Date <span className="text-destructive">*</span>
                </label>
                <input
                  type="text"
                  value={cardDetails.expiry}
                  onChange={(e) =>
                    setCardDetails({ ...cardDetails, expiry: e.target.value })
                  }
                  placeholder="MM/YY"
                  className="w-full px-4 py-2 border rounded-md"
                  maxLength={5}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  CVV <span className="text-destructive">*</span>
                </label>
                <input
                  type="text"
                  value={cardDetails.cvv}
                  onChange={(e) =>
                    setCardDetails({ ...cardDetails, cvv: e.target.value })
                  }
                  placeholder="123"
                  className="w-full px-4 py-2 border rounded-md"
                  maxLength={4}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Cardholder Name <span className="text-destructive">*</span>
              </label>
              <input
                type="text"
                value={cardDetails.name}
                onChange={(e) =>
                  setCardDetails({ ...cardDetails, name: e.target.value })
                }
                placeholder="John Doe"
                className="w-full px-4 py-2 border rounded-md"
              />
            </div>
          </div>
        )}

        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Lock className="h-4 w-4" />
          <span>Your payment information is secure and encrypted</span>
        </div>

        <div className="flex gap-4">
          <button
            type="button"
            onClick={() => window.history.back()}
            className="flex-1 px-6 py-3 border rounded-md font-semibold hover:bg-accent transition-colors"
          >
            Back
          </button>
          <button
            type="submit"
            className="flex-1 bg-primary text-primary-foreground px-6 py-3 rounded-md font-semibold hover:bg-primary/90 transition-colors"
          >
            Continue to Review
          </button>
        </div>
      </form>
    </div>
  );
}

