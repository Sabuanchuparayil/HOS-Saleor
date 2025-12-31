"use client";

import { useState } from "react";
import { useQuery } from "@apollo/client/react";
import { GET_USER_ADDRESSES } from "@/lib/graphql/queries";
import { MapPin, Plus, Edit, Trash2, Loader2 } from "lucide-react";
import { AddressForm } from "./AddressForm";

export function AddressBook() {
  const [showForm, setShowForm] = useState(false);
  const [editingAddress, setEditingAddress] = useState<any>(null);

  const { data, loading, error, refetch } = useQuery(GET_USER_ADDRESSES, {
    fetchPolicy: "cache-and-network",
  });

  const addresses = (data as any)?.me?.addresses || [];

  const handleEdit = (address: any) => {
    setEditingAddress(address);
    setShowForm(true);
  };

  const handleAdd = () => {
    setEditingAddress(null);
    setShowForm(true);
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingAddress(null);
    refetch();
  };

  if (loading && !data) {
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
          <h1 className="text-4xl font-bold mb-2">Address Book</h1>
          <p className="text-muted-foreground">
            Manage your shipping addresses
          </p>
        </div>
        <button
          onClick={handleAdd}
          className="flex items-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded-md font-semibold hover:bg-primary/90 transition-colors"
        >
          <Plus className="h-5 w-5" />
          Add Address
        </button>
      </div>

      {showForm && (
        <div className="mb-8">
          <AddressForm
            address={editingAddress}
            onClose={handleFormClose}
            onSuccess={handleFormClose}
          />
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
          <p className="text-destructive">{error.message}</p>
        </div>
      )}

      {addresses.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {addresses.map((address: any) => (
            <div
              key={address.id}
              className="border rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-2">
                  <MapPin className="h-5 w-5 text-primary" />
                  <h3 className="font-semibold">
                    {address.firstName} {address.lastName}
                  </h3>
                  {address.isDefaultShipping && (
                    <span className="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full">
                      Default
                    </span>
                  )}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEdit(address)}
                    className="p-2 hover:bg-accent rounded-md transition-colors"
                    aria-label="Edit address"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    className="p-2 hover:bg-destructive/10 text-destructive rounded-md transition-colors"
                    aria-label="Delete address"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
              <div className="text-sm text-muted-foreground space-y-1">
                <p>{address.streetAddress1}</p>
                {address.streetAddress2 && <p>{address.streetAddress2}</p>}
                <p>
                  {address.city}, {address.postalCode}
                </p>
                <p>
                  {address.countryArea && `${address.countryArea}, `}
                  {address.country?.name || address.country?.code}
                </p>
                {address.phone && <p>{address.phone}</p>}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 border rounded-lg">
          <MapPin className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground mb-4">No addresses saved</p>
          <button
            onClick={handleAdd}
            className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded-md font-semibold hover:bg-primary/90 transition-colors"
          >
            <Plus className="h-5 w-5" />
            Add Your First Address
          </button>
        </div>
      )}
    </div>
  );
}

