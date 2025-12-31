"use client";

import { useQuery } from "@apollo/client/react";
import { GET_USER_ORDERS } from "@/lib/graphql/queries";
import Link from "next/link";
import { formatPrice, formatDate } from "@/lib/utils";
import { Package, Loader2 } from "lucide-react";
import { useState } from "react";

export function OrderHistory() {
  const [page, setPage] = useState(1);
  const itemsPerPage = 10;

  const { data, loading, error, fetchMore } = useQuery(GET_USER_ORDERS, {
    variables: { first: itemsPerPage },
    fetchPolicy: "cache-and-network",
  });

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive mb-4">Error loading orders</p>
        <p className="text-sm text-muted-foreground">{error.message}</p>
      </div>
    );
  }

  const orders = (data as any)?.me?.orders?.edges?.map((edge: any) => edge.node) || [];
  const pageInfo = (data as any)?.me?.orders?.pageInfo;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Order History</h1>
        <p className="text-muted-foreground">
          View and track all your orders
        </p>
      </div>

      {orders.length > 0 ? (
        <>
          <div className="space-y-4">
            {orders.map((order: any) => (
              <Link
                key={order.id}
                href={`/account/orders/${order.id}`}
                className="block border rounded-lg p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-2">
                      <h3 className="font-semibold text-lg">
                        Order #{order.number || order.id.slice(-8)}
                      </h3>
                      <span
                        className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                          order.status === "FULFILLED"
                            ? "bg-green-100 text-green-800"
                            : order.status === "UNFULFILLED"
                            ? "bg-yellow-100 text-yellow-800"
                            : order.status === "CANCELED"
                            ? "bg-red-100 text-red-800"
                            : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {order.status || "Processing"}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">
                      Placed on {formatDate(order.created)}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {order.lines?.length || 0} item(s)
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-lg mb-2">
                      {order.total?.gross
                        ? formatPrice(order.total.gross.amount / 100, order.total.gross.currency)
                        : "N/A"}
                    </p>
                    <p className="text-sm text-primary hover:underline">View Details →</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {pageInfo?.hasNextPage && (
            <div className="mt-8 text-center">
              <button
                onClick={() => {
                  fetchMore({
                    variables: {
                      after: pageInfo.endCursor,
                    },
                  });
                  setPage(page + 1);
                }}
                disabled={loading}
                className="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
              >
                {loading ? "Loading..." : "Load More"}
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-12 border rounded-lg">
          <Package className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground mb-4">No orders found</p>
          <Link
            href="/products"
            className="inline-flex items-center justify-center rounded-lg bg-primary px-6 py-3 text-primary-foreground font-semibold hover:bg-primary/90 transition-colors"
          >
            Start Shopping
          </Link>
        </div>
      )}
    </div>
  );
}

