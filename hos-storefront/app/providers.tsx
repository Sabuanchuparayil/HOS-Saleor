"use client";

import { ApolloProvider } from "@apollo/client/react";
import { apolloClient } from "@/lib/apollo-client";
import { SeoDefaults } from "@/components/seo/SeoDefaults";
import { ThemeProvider } from "@/components/theme/ThemeProvider";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <ApolloProvider client={apolloClient}>
        <SeoDefaults />
        {children}
      </ApolloProvider>
    </ThemeProvider>
  );
}

