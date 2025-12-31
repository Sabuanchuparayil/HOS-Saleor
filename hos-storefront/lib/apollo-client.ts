import { ApolloClient, InMemoryCache, createHttpLink } from "@apollo/client";
import { setContext } from "@apollo/client/link/context";

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
  link: authLink.concat(httpLink),
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

