"use client";

import { DefaultSeo } from "next-seo";

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL || "https://hos-storefront-production.up.railway.app";

export function SeoDefaults() {
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


