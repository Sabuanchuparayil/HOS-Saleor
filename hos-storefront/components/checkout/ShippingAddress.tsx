"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation } from "@apollo/client/react";
import {
  UPDATE_CHECKOUT_DELIVERY_METHOD,
  UPDATE_CHECKOUT_SHIPPING_ADDRESS,
} from "@/lib/graphql/mutations";
import { formatPrice } from "@/lib/utils";

const addressSchema = z.object({
  firstName: z.string().min(1, "First name is required"),
  lastName: z.string().min(1, "Last name is required"),
  streetAddress1: z.string().min(1, "Address is required"),
  streetAddress2: z.string().optional(),
  city: z.string().min(1, "City is required"),
  postalCode: z.string().min(1, "Postal code is required"),
  country: z.string().min(1, "Country is required"),
  countryArea: z.string().optional(),
  phone: z.string().optional(),
});

type AddressFormData = z.infer<typeof addressSchema>;

interface ShippingAddressProps {
  checkout: any;
  onSubmit: (address: AddressFormData) => void;
  refetchCheckout?: () => Promise<any>;
}

export function ShippingAddress({ checkout, onSubmit, refetchCheckout }: ShippingAddressProps) {
  const [updateAddress] = useMutation(UPDATE_CHECKOUT_SHIPPING_ADDRESS);
  const [updateDeliveryMethod, { loading: deliveryUpdating }] = useMutation(
    UPDATE_CHECKOUT_DELIVERY_METHOD
  );
  const [isGuest, setIsGuest] = useState(true);
  const [addressSaved, setAddressSaved] = useState(false);
  const [selectedShippingMethodId, setSelectedShippingMethodId] = useState<string | null>(
    checkout?.delivery?.shippingMethod?.id || null
  );

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<AddressFormData>({
    resolver: zodResolver(addressSchema),
    defaultValues: {
      country: "US",
    },
  });

  const onFormSubmit = async (data: AddressFormData) => {
    try {
      if (checkout.id) {
        await updateAddress({
          variables: {
            checkoutId: checkout.id,
            shippingAddress: {
              firstName: data.firstName,
              lastName: data.lastName,
              streetAddress1: data.streetAddress1,
              streetAddress2: data.streetAddress2,
              city: data.city,
              postalCode: data.postalCode,
              country: data.country,
              countryArea: data.countryArea,
              phone: data.phone,
            },
          },
        });
      }
      // Refresh checkout so shipping methods are recalculated for the destination
      if (refetchCheckout) {
        await refetchCheckout();
      }
      setAddressSaved(true);

      // If shipping isn't required, allow moving on immediately
      if (checkout?.isShippingRequired === false) {
        onSubmit(data);
      }
    } catch (error) {
      console.error("Error updating shipping address:", error);
      alert("There was an error updating your shipping address. Please try again.");
    }
  };

  const shippingMethods: any[] = checkout?.shippingMethods || [];
  const shippingSelectedName = checkout?.delivery?.shippingMethod?.name;

  const handleContinue = async (data: AddressFormData) => {
    // Require method selection when shipping is required
    if (checkout?.isShippingRequired !== false) {
      if (!selectedShippingMethodId) {
        alert("Please select a shipping method.");
        return;
      }

      try {
        await updateDeliveryMethod({
          variables: {
            checkoutId: checkout.id,
            deliveryMethodId: selectedShippingMethodId,
          },
        });
        if (refetchCheckout) {
          await refetchCheckout();
        }
      } catch (error) {
        console.error("Error updating delivery method:", error);
        alert("There was an error selecting your shipping method. Please try again.");
        return;
      }
    }

    onSubmit(data);
  };

  return (
    <div className="border rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-6">Shipping Address</h2>

      {isGuest && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-sm text-blue-800">
            You're checking out as a guest. You can create an account after your order.
          </p>
        </div>
      )}

      <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              First Name <span className="text-destructive">*</span>
            </label>
            <input
              {...register("firstName")}
              className="w-full px-4 py-2 border rounded-md"
              placeholder="John"
            />
            {errors.firstName && (
              <p className="text-sm text-destructive mt-1">{errors.firstName.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Last Name <span className="text-destructive">*</span>
            </label>
            <input
              {...register("lastName")}
              className="w-full px-4 py-2 border rounded-md"
              placeholder="Doe"
            />
            {errors.lastName && (
              <p className="text-sm text-destructive mt-1">{errors.lastName.message}</p>
            )}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Street Address <span className="text-destructive">*</span>
          </label>
          <input
            {...register("streetAddress1")}
            className="w-full px-4 py-2 border rounded-md"
            placeholder="123 Main St"
          />
          {errors.streetAddress1 && (
            <p className="text-sm text-destructive mt-1">{errors.streetAddress1.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Apartment, suite, etc. (optional)</label>
          <input
            {...register("streetAddress2")}
            className="w-full px-4 py-2 border rounded-md"
            placeholder="Apt 4B"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              City <span className="text-destructive">*</span>
            </label>
            <input
              {...register("city")}
              className="w-full px-4 py-2 border rounded-md"
              placeholder="New York"
            />
            {errors.city && (
              <p className="text-sm text-destructive mt-1">{errors.city.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Postal Code <span className="text-destructive">*</span>
            </label>
            <input
              {...register("postalCode")}
              className="w-full px-4 py-2 border rounded-md"
              placeholder="10001"
            />
            {errors.postalCode && (
              <p className="text-sm text-destructive mt-1">{errors.postalCode.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Country <span className="text-destructive">*</span>
            </label>
            <select
              {...register("country")}
              className="w-full px-4 py-2 border rounded-md"
            >
              <option value="US">United States</option>
              <option value="GB">United Kingdom</option>
              <option value="CA">Canada</option>
              <option value="AU">Australia</option>
              <option value="MY">Malaysia</option>
              <option value="AE">United Arab Emirates</option>
            </select>
            {errors.country && (
              <p className="text-sm text-destructive mt-1">{errors.country.message}</p>
            )}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Phone (optional)</label>
          <input
            {...register("phone")}
            type="tel"
            className="w-full px-4 py-2 border rounded-md"
            placeholder="+1 (555) 123-4567"
          />
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-primary text-primary-foreground px-6 py-3 rounded-md font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50"
        >
          {isSubmitting ? "Saving address..." : "Save Address"}
        </button>
      </form>

      {/* Shipping Method Selection */}
      {checkout?.isShippingRequired !== false && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-3">Shipping Method</h3>

          {!addressSaved && shippingMethods.length === 0 && (
            <p className="text-sm text-muted-foreground">
              Save your address to see available shipping methods.
            </p>
          )}

          {shippingMethods.length > 0 && (
            <div className="space-y-3">
              {shippingMethods.map((method: any) => {
                const price = method.price || { amount: 0, currency: "USD" };
                const days =
                  method.minimumDeliveryDays || method.maximumDeliveryDays
                    ? `${method.minimumDeliveryDays ?? ""}${
                        method.minimumDeliveryDays && method.maximumDeliveryDays ? "-" : ""
                      }${method.maximumDeliveryDays ?? ""} days`
                    : null;

                return (
                  <label
                    key={method.id}
                    className="flex items-start gap-3 border rounded-md p-4 cursor-pointer hover:bg-accent/30 transition-colors"
                  >
                    <input
                      type="radio"
                      name="shippingMethod"
                      value={method.id}
                      checked={selectedShippingMethodId === method.id}
                      onChange={() => setSelectedShippingMethodId(method.id)}
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <div className="flex items-center justify-between gap-4">
                        <div className="font-medium">{method.name}</div>
                        <div className="text-sm font-semibold">
                          {formatPrice(price.amount, price.currency)}
                        </div>
                      </div>
                      {days && (
                        <div className="text-xs text-muted-foreground mt-1">
                          Estimated delivery: {days}
                        </div>
                      )}
                    </div>
                  </label>
                );
              })}
            </div>
          )}

          <div className="mt-6">
            <button
              type="button"
              disabled={
                deliveryUpdating ||
                (checkout?.isShippingRequired !== false &&
                  (shippingMethods.length === 0 || !selectedShippingMethodId))
              }
              onClick={handleSubmit(handleContinue)}
              className="w-full bg-primary text-primary-foreground px-6 py-3 rounded-md font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              {deliveryUpdating
                ? "Selecting shipping..."
                : shippingSelectedName
                ? "Continue to Payment"
                : "Select Shipping & Continue"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}


