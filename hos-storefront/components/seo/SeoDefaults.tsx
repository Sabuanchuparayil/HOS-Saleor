"use client";

import * as NextSeo from "next-seo";

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL || "https://hos-storefront-production.up.railway.app";

export function SeoDefaults() {
  // Turbopack/ESM: `next-seo` exports can vary by version/build.
  // Avoid hard failing the build by accessing via namespace import.
  const DefaultSeo = (NextSeo as unknown as { DefaultSeo?: React.ComponentType<any> })
    .DefaultSeo;

  if (!DefaultSeo) {
    // We rely on Next.js `metadata` for defaults; this is an optional enhancer.
    return null;
  }

  return (
    <DefaultSeo
      titleTemplate="%s | House of Spells"
      defaultTitle="House of Spells Marketplace"
      description="Discover magical products from authorized sellers worldwide"
      canonical={siteUrl}
      openGraph={{
        type: "website",
        locale: "en_US",
        url: siteUrl,
        siteName: "House of Spells Marketplace",
      }}
      twitter={{
        cardType: "summary_large_image",
      }}
      additionalMetaTags={[
        { name: "application-name", content: "House of Spells Marketplace" },
        { name: "theme-color", content: "#7c3aed" },
      ]}
    />
  );
}


