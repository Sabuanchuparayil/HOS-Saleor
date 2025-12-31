import { ApolloClient, InMemoryCache, createHttpLink } from "@apollo/client";
import { setContext } from "@apollo/client/link/context";
import { onError } from "@apollo/client/link/error";

// Error link for better error logging
const errorLink = onError(({ graphQLErrors, networkError, operation, forward }: any) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path, extensions }: any) => {
      console.error(
        `[GraphQL error]: Message: ${message}, Location: ${JSON.stringify(locations)}, Path: ${JSON.stringify(path)}`,
        extensions
      );
    });
  }
  if (networkError) {
    console.error(`[Network error]: ${networkError}`);
    // Log response if available
    if ('response' in networkError && networkError.response) {
      console.error('Response status:', networkError.response.status);
      console.error('Response headers:', networkError.response.headers);
      // Try to read response body
      if ('text' in networkError.response) {
        networkError.response.text().then((text: string) => {
          console.error('Response body:', text);
        }).catch(() => {});
      }
    }
  }
});

const httpLink = createHttpLink({
  uri: process.env.NEXT_PUBLIC_SALEOR_API_URL || "https://hos-saleor-production.up.railway.app/graphql/",
  credentials: "same-origin",
  fetchOptions: {
    mode: "cors",
  },
});

const authLink = setContext((_, { headers }) => {
  // Get the authentication token from localStorage if it exists
  const token = typeof window !== "undefined" ? localStorage.getItem("authToken") : null;
  
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : "",
    },
  };
});

export const apolloClient = new ApolloClient({
  link: errorLink.concat(authLink.concat(httpLink)),
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          products: {
            keyArgs: ["filter", "sortBy"],
            merge(existing = [], incoming) {
              return incoming;
            },
          },
        },
      },
    },
  }),
  defaultOptions: {
    watchQuery: {
      errorPolicy: "all",
    },
    query: {
      errorPolicy: "all",
    },
  },
});
