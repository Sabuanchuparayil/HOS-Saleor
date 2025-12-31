"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@apollo/client/react";
import { GET_USER_RETURNS, GET_USER_ORDERS } from "@/lib/graphql/queries";
import { CREATE_RETURN_REQUEST } from "@/lib/graphql/mutations";
import { Package, Plus, Loader2, AlertCircle } from "lucide-react";
import { formatDate, formatPrice } from "@/lib/utils";
import { ReturnRequestForm } from "./ReturnRequestForm";

export function ReturnsManagement() {
  const [showForm, setShowForm] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<any>(null);

  const { data: returnsData, loading: returnsLoading } = useQuery(GET_USER_RETURNS, {
    fetchPolicy: "cache-and-network",
  });

  const { data: ordersData } = useQuery(GET_USER_ORDERS, {
    variables: { first: 20 },
    skip: !showForm,
  });

  const returnRequests = (returnsData as any)?.me?.returnRequests?.edges?.map(
    (edge: any) => edge.node
  ) || [];

  const handleCreateReturn = (order: any) => {
    setSelectedOrder(order);
    setShowForm(true);
  };

  const handleFormClose = () => {
    setShowForm(false);
    setSelectedOrder(null);
  };

  if (returnsLoading && !returnsData) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">Returns</h1>
          <p className="text-muted-foreground">
            Manage your return requests
          </p>
        </div>
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded-md font-semibold hover:bg-primary/90 transition-colors"
          >
            <Plus className="h-5 w-5" />
            Request Return
          </button>
        )}
      </div>

      {showForm && (
        <div className="mb-8">
          <ReturnRequestForm
            order={selectedOrder}
            orders={(ordersData as any)?.me?.orders?.edges?.map((edge: any) => edge.node) || []}
            onClose={handleFormClose}
            onSuccess={handleFormClose}
          />
        </div>
      )}

      {returnRequests.length > 0 ? (
        <div className="space-y-4">
          {returnRequests.map((request: any) => (
            <div
              key={request.id}
              className="border rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-semibold text-lg mb-1">
                    Return Request #{request.id.slice(-8)}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Created on {formatDate(request.created)}
                  </p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${
                    request.status === "APPROVED"
                      ? "bg-green-100 text-green-800"
                      : request.status === "REJECTED"
                      ? "bg-red-100 text-red-800"
                      : request.status === "COMPLETED"
                      ? "bg-blue-100 text-blue-800"
                      : "bg-yellow-100 text-yellow-800"
                  }`}
                >
                  {request.status || "PENDING"}
                </span>
              </div>

              <div className="space-y-2 text-sm">
                <p>
                  <span className="font-medium">Order:</span>{" "}
                  {request.order?.number || request.orderId}
                </p>
                {request.reason && (
                  <p>
                    <span className="font-medium">Reason:</span> {request.reason}
                  </p>
                )}
                {request.notes && (
                  <p>
                    <span className="font-medium">Notes:</span> {request.notes}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 border rounded-lg">
          <Package className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground mb-4">No return requests</p>
          {!showForm && (
            <button
              onClick={() => setShowForm(true)}
              className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded-md font-semibold hover:bg-primary/90 transition-colors"
            >
              <Plus className="h-5 w-5" />
              Request Your First Return
            </button>
          )}
        </div>
      )}
    </div>
  );
}

