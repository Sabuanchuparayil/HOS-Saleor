"use client";

import Link from "next/link";
import { ShoppingCart, Search, User } from "lucide-react";
import { SearchBar } from "./SearchBar";

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-2xl font-bold">✨ House of Spells</span>
          </Link>
          <nav className="hidden md:flex items-center gap-6">
            <Link
              href="/products"
              className="text-sm font-medium transition-colors hover:text-primary"
            >
              Products
            </Link>
            <Link
              href="/sellers"
              className="text-sm font-medium transition-colors hover:text-primary"
            >
              Sellers
            </Link>
            <Link
              href="/collections"
              className="text-sm font-medium transition-colors hover:text-primary"
            >
              Collections
            </Link>
            <Link
              href="/discounts"
              className="text-sm font-medium transition-colors hover:text-primary"
            >
              Discounts
            </Link>
          </nav>
        </div>
        <div className="flex items-center gap-4 flex-1 justify-end">
          <div className="hidden md:block flex-1 max-w-2xl">
            <SearchBar />
          </div>
          <button
            type="button"
            className="md:hidden p-2 rounded-md hover:bg-accent"
            aria-label="Search"
          >
            <Search className="h-5 w-5" />
          </button>
          <Link
            href="/account"
            className="p-2 rounded-md hover:bg-accent"
            aria-label="Account"
          >
            <User className="h-5 w-5" />
          </Link>
          <Link
            href="/cart"
            className="relative p-2 rounded-md hover:bg-accent"
            aria-label="Shopping cart"
          >
            <ShoppingCart className="h-5 w-5" />
            <span className="absolute top-0 right-0 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[10px] font-medium text-primary-foreground">
              0
            </span>
          </Link>
        </div>
      </div>
    </header>
  );
}

