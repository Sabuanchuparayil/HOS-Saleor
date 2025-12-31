"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation } from "@apollo/client/react";
import { SUBSCRIBE_NEWSLETTER } from "@/lib/graphql/mutations";
import { Mail, Check } from "lucide-react";

const newsletterSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
});

type NewsletterFormData = z.infer<typeof newsletterSchema>;

export function NewsletterSignup() {
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [subscribeNewsletter] = useMutation(SUBSCRIBE_NEWSLETTER);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<NewsletterFormData>({
    resolver: zodResolver(newsletterSchema),
  });

  const onSubmit = async (data: NewsletterFormData) => {
    try {
      const result = await subscribeNewsletter({
        variables: {
          email: data.email,
          source: "homepage",
        },
      });

      const errors = (result.data as any)?.newsletterSubscribe?.errors;
      if (errors && errors.length > 0) {
        alert(`Error: ${errors[0].message}`);
      } else {
        setIsSubscribed(true);
        reset();
        setTimeout(() => setIsSubscribed(false), 5000);
      }
    } catch (error: any) {
      console.error("Error subscribing:", error);
      alert("There was an error subscribing. Please try again.");
    }
  };

  return (
    <div className="bg-gradient-to-r from-purple-900 to-indigo-900 text-white rounded-lg p-8">
      <div className="max-w-2xl mx-auto text-center">
        <Mail className="h-12 w-12 mx-auto mb-4" />
        <h2 className="text-3xl font-bold mb-2">Stay Updated</h2>
        <p className="text-lg text-white/90 mb-6">
          Subscribe to our newsletter for the latest products, deals, and magical updates
        </p>
        {isSubscribed ? (
          <div className="flex items-center justify-center gap-2 text-green-300">
            <Check className="h-5 w-5" />
            <p className="font-medium">Thank you for subscribing!</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col sm:flex-row gap-4">
            <input
              {...register("email")}
              type="email"
              placeholder="Enter your email"
              className="flex-1 px-4 py-3 rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-white"
            />
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-8 py-3 bg-white text-purple-900 rounded-lg font-semibold hover:bg-gray-100 transition-colors disabled:opacity-50"
            >
              {isSubmitting ? "Subscribing..." : "Subscribe"}
            </button>
          </form>
        )}
        {errors.email && (
          <p className="mt-2 text-sm text-red-300">{errors.email.message}</p>
        )}
      </div>
    </div>
  );
}

