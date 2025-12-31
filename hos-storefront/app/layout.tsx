import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: {
    default: "House of Spells Marketplace",
    template: "%s | House of Spells",
  },
  description: "Discover magical products from authorized sellers worldwide",
  keywords: ["magic", "spells", "marketplace", "B2B", "B2C"],
  authors: [{ name: "House of Spells" }],
  openGraph: {
    type: "website",
    locale: "en_US",
    url: process.env.NEXT_PUBLIC_SITE_URL || "https://hos-marketplaceweb-production.up.railway.app",
    siteName: "House of Spells Marketplace",
    title: "House of Spells Marketplace",
    description: "Discover magical products from authorized sellers worldwide",
  },
  twitter: {
    card: "summary_large_image",
    title: "House of Spells Marketplace",
    description: "Discover magical products from authorized sellers worldwide",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
