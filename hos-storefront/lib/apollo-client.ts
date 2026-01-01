import { ApolloClient, InMemoryCache, createHttpLink } from "@apollo/client";
import { setContext } from "@apollo/client/link/context";
import { onError } from "@apollo/client/link/error";

const _APOLLO_DEBUG = process.env.NEXT_PUBLIC_APOLLO_DEBUG === "1";

// Error link for optional debugging. Avoid noisy logs in production by default.
const errorLink = onError(({ graphQLErrors, networkError, operation }: any) => {
  if (!_APOLLO_DEBUG) {
    return;
  }

  console.group("Apollo Client Error");
  console.log("Operation:", operation?.operationName || "Unknown");
  console.log("Variables:", operation?.variables || {});

  if (graphQLErrors?.length) {
    console.group("GraphQL Errors");
    graphQLErrors.forEach(({ message, locations, path, extensions }: any) => {
      console.error({ message, locations, path, extensions });
    });
    console.groupEnd();
  }

  if (networkError) {
    console.error("Network Error:", networkError);
  }

  console.groupEnd();
});

const httpLink = createHttpLink({
  uri: process.env.NEXT_PUBLIC_SALEOR_API_URL || "https://hos-saleor-production.up.railway.app/graphql/",
  // We use Bearer tokens (localStorage) rather than cookies, so omit credentials.
  credentials: "omit",
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
