import { ApolloClient, InMemoryCache, createHttpLink } from "@apollo/client";
import { setContext } from "@apollo/client/link/context";
import { onError } from "@apollo/client/link/error";

// Error link for better error logging
const errorLink = onError(({ graphQLErrors, networkError, operation, forward }: any) => {
  console.group('🔴 Apollo Client Error');
  console.log('Operation:', operation?.operationName || 'Unknown');
  console.log('Variables:', operation?.variables || {});
  
  if (graphQLErrors) {
    console.group('GraphQL Errors:');
    graphQLErrors.forEach(({ message, locations, path, extensions }: any) => {
      console.error('Message:', message);
      console.error('Locations:', locations);
      console.error('Path:', path);
      console.error('Extensions:', extensions);
    });
    console.groupEnd();
  }
  
  if (networkError) {
    console.group('Network Error:');
    console.error('Error:', networkError);
    console.error('Message:', (networkError as any).message);
    
    // Log response if available
    if ('response' in networkError && networkError.response) {
      const response = networkError.response as any;
      console.error('Response status:', response.status);
      console.error('Response statusText:', response.statusText);
      console.error('Response headers:', response.headers);
      
      // Try to read response body
      if (response.text) {
        response.text().then((text: string) => {
          console.error('Response body:', text);
          try {
            const json = JSON.parse(text);
            console.error('Response JSON:', json);
          } catch (e) {
            // Not JSON, that's fine
          }
        }).catch((err: any) => {
          console.error('Error reading response body:', err);
        });
      } else if (response.body) {
        console.error('Response body (stream):', response.body);
      }
    }
    
    // Log request details
    if ('request' in networkError && networkError.request) {
      console.error('Request URL:', (networkError.request as any).url);
      console.error('Request method:', (networkError.request as any).method);
    }
    
    console.groupEnd();
  }
  
  console.groupEnd();
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
