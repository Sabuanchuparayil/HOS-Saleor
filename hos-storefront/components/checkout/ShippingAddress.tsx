"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation } from "@apollo/client/react";
import { UPDATE_CHECKOUT_SHIPPING_ADDRESS } from "@/lib/graphql/mutations";

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
}

export function ShippingAddress({ checkout, onSubmit }: ShippingAddressProps) {
  const [updateAddress] = useMutation(UPDATE_CHECKOUT_SHIPPING_ADDRESS);
  const [isGuest, setIsGuest] = useState(true);

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
      onSubmit(data);
    } catch (error) {
      console.error("Error updating shipping address:", error);
      alert("There was an error updating your shipping address. Please try again.");
    }
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
          {isSubmitting ? "Processing..." : "Continue to Payment"}
        </button>
      </form>
    </div>
  );
}

