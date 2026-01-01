"use client";

import Link from "next/link";
import { ChevronRight, Home } from "lucide-react";
import { useEffect } from "react";
import { generateBreadcrumbJSONLD } from "@/lib/seo/jsonld";

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
}

export function Breadcrumbs({ items }: BreadcrumbsProps) {
  useEffect(() => {
    const siteUrl =
      process.env.NEXT_PUBLIC_SITE_URL ||
      "https://hos-storefront-production.up.railway.app";

    const jsonLdItems = [
      { name: "Home", url: siteUrl },
      ...items
        .filter((i) => !!i.href)
        .map((i) => ({
          name: i.label,
          url: `${siteUrl}${i.href}`,
        })),
    ];

    const jsonLd = generateBreadcrumbJSONLD(jsonLdItems);
    const script = document.createElement("script");
    script.type = "application/ld+json";
    script.setAttribute("data-breadcrumbs-jsonld", "true");
    script.text = JSON.stringify(jsonLd);
    document.head.appendChild(script);

    return () => {
      script.parentNode?.removeChild(script);
    };
  }, [items]);

  return (
    <nav aria-label="Breadcrumb" className="mb-6">
      <ol className="flex items-center gap-2 text-sm text-muted-foreground">
        <li>
          <Link
            href="/"
            className="hover:text-foreground transition-colors flex items-center gap-1"
          >
            <Home className="h-4 w-4" />
            <span className="sr-only">Home</span>
          </Link>
        </li>
        {items.map((item, index) => (
          <li key={index} className="flex items-center gap-2">
            <ChevronRight className="h-4 w-4" />
            {item.href ? (
              <Link
                href={item.href}
                className="hover:text-foreground transition-colors"
              >
                {item.label}
              </Link>
            ) : (
              <span className="text-foreground font-medium">{item.label}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}


