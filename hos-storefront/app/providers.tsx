"use client";

import { ApolloProvider } from "@apollo/client/react";
import { apolloClient } from "@/lib/apollo-client";
import { SeoDefaults } from "@/components/seo/SeoDefaults";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ApolloProvider client={apolloClient}>
      <SeoDefaults />
      {children}
    </ApolloProvider>
  );
}

