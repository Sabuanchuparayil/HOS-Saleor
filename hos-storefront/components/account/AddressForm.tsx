"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation } from "@apollo/client/react";
import { CREATE_ADDRESS, UPDATE_ADDRESS } from "@/lib/graphql/mutations";
import { X } from "lucide-react";

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
  isDefaultShipping: z.boolean().optional(),
});

type AddressFormData = z.infer<typeof addressSchema>;

interface AddressFormProps {
  address?: any;
  onClose: () => void;
  onSuccess: () => void;
}

export function AddressForm({ address, onClose, onSuccess }: AddressFormProps) {
  const [createAddress] = useMutation(CREATE_ADDRESS);
  const [updateAddress] = useMutation(UPDATE_ADDRESS);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<AddressFormData>({
    resolver: zodResolver(addressSchema),
    defaultValues: address
      ? {
          firstName: address.firstName,
          lastName: address.lastName,
          streetAddress1: address.streetAddress1,
          streetAddress2: address.streetAddress2,
          city: address.city,
          postalCode: address.postalCode,
          country: address.country?.code || "US",
          countryArea: address.countryArea,
          phone: address.phone,
          isDefaultShipping: address.isDefaultShipping,
        }
      : {
          country: "US",
        },
  });

  const onSubmit = async (data: AddressFormData) => {
    setIsSubmitting(true);
    try {
      if (address) {
        await updateAddress({
          variables: {
            id: address.id,
            input: data,
          },
        });
      } else {
        await createAddress({
          variables: {
            input: data,
          },
        });
      }
      onSuccess();
    } catch (error: any) {
      console.error("Error saving address:", error);
      alert("There was an error saving the address. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="border rounded-lg p-6 bg-background">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">
          {address ? "Edit Address" : "Add New Address"}
        </h2>
        <button
          onClick={onClose}
          className="p-2 hover:bg-accent rounded-md transition-colors"
          aria-label="Close"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              First Name <span className="text-destructive">*</span>
            </label>
            <input
              {...register("firstName")}
              className="w-full px-4 py-2 border rounded-md"
            />
            {errors.firstName && (
              <p className="text-sm text-destructive mt-1">
                {errors.firstName.message}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Last Name <span className="text-destructive">*</span>
            </label>
            <input
              {...register("lastName")}
              className="w-full px-4 py-2 border rounded-md"
            />
            {errors.lastName && (
              <p className="text-sm text-destructive mt-1">
                {errors.lastName.message}
              </p>
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
          />
          {errors.streetAddress1 && (
            <p className="text-sm text-destructive mt-1">
              {errors.streetAddress1.message}
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Apartment, suite, etc. (optional)
          </label>
          <input
            {...register("streetAddress2")}
            className="w-full px-4 py-2 border rounded-md"
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
            />
            {errors.city && (
              <p className="text-sm text-destructive mt-1">
                {errors.city.message}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Postal Code <span className="text-destructive">*</span>
            </label>
            <input
              {...register("postalCode")}
              className="w-full px-4 py-2 border rounded-md"
            />
            {errors.postalCode && (
              <p className="text-sm text-destructive mt-1">
                {errors.postalCode.message}
              </p>
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
              <p className="text-sm text-destructive mt-1">
                {errors.country.message}
              </p>
            )}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Phone (optional)</label>
          <input
            {...register("phone")}
            type="tel"
            className="w-full px-4 py-2 border rounded-md"
          />
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            {...register("isDefaultShipping")}
            className="rounded"
          />
          <label className="text-sm">Set as default shipping address</label>
        </div>

        <div className="flex gap-4 pt-4">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 px-6 py-3 border rounded-md font-semibold hover:bg-accent transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="flex-1 bg-primary text-primary-foreground px-6 py-3 rounded-md font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50"
          >
            {isSubmitting ? "Saving..." : address ? "Update Address" : "Add Address"}
          </button>
        </div>
      </form>
    </div>
  );
}

