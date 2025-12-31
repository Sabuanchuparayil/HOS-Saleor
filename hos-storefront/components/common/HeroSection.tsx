import Link from "next/link";
import { ArrowRight } from "lucide-react";

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 text-white">
      <div className="container relative z-10 py-24 md:py-32">
        <div className="max-w-3xl">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            Welcome to House of Spells
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-gray-200">
            Discover magical products from authorized sellers worldwide. 
            Your trusted marketplace for B2B and B2C magical goods.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              href="/products"
              className="inline-flex items-center justify-center rounded-lg bg-white px-8 py-3 text-lg font-semibold text-purple-900 transition-colors hover:bg-gray-100"
            >
              Shop Now
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
            <Link
              href="/sellers"
              className="inline-flex items-center justify-center rounded-lg border-2 border-white px-8 py-3 text-lg font-semibold text-white transition-colors hover:bg-white/10"
            >
              Browse Sellers
            </Link>
          </div>
        </div>
      </div>
      <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]"></div>
    </section>
  );
}

