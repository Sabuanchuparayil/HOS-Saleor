"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation } from "@apollo/client/react";
import { CREATE_RETURN_REQUEST } from "@/lib/graphql/mutations";
import { X } from "lucide-react";

const returnRequestSchema = z.object({
  orderId: z.string().min(1, "Please select an order"),
  reason: z.string().min(1, "Please provide a reason"),
  notes: z.string().optional(),
});

type ReturnRequestFormData = z.infer<typeof returnRequestSchema>;

interface ReturnRequestFormProps {
  order?: any;
  orders: any[];
  onClose: () => void;
  onSuccess: () => void;
}

export function ReturnRequestForm({
  order,
  orders,
  onClose,
  onSuccess,
}: ReturnRequestFormProps) {
  const [createReturn] = useMutation(CREATE_RETURN_REQUEST);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ReturnRequestFormData>({
    resolver: zodResolver(returnRequestSchema),
    defaultValues: {
      orderId: order?.id || "",
    },
  });

  const onSubmit = async (data: ReturnRequestFormData) => {
    setIsSubmitting(true);
    try {
      const { data: result } = await createReturn({
        variables: {
          input: {
            orderId: data.orderId,
            reason: data.reason,
            notes: data.notes,
          },
        },
      });

      const errors = (result as any)?.returnRequestCreate?.errors;
      if (errors && errors.length > 0) {
        alert(`Error: ${errors[0].message}`);
      } else {
        onSuccess();
      }
    } catch (error: any) {
      console.error("Error creating return request:", error);
      alert("There was an error creating the return request. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="border rounded-lg p-6 bg-background">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Request Return</h2>
        <button
          onClick={onClose}
          className="p-2 hover:bg-accent rounded-md transition-colors"
          aria-label="Close"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">
            Select Order <span className="text-destructive">*</span>
          </label>
          <select
            {...register("orderId")}
            className="w-full px-4 py-2 border rounded-md"
            disabled={!!order}
          >
            <option value="">Select an order...</option>
            {orders.map((ord) => (
              <option key={ord.id} value={ord.id}>
                Order #{ord.number || ord.id.slice(-8)} -{" "}
                {new Date(ord.created).toLocaleDateString()}
              </option>
            ))}
          </select>
          {errors.orderId && (
            <p className="text-sm text-destructive mt-1">
              {errors.orderId.message}
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Reason for Return <span className="text-destructive">*</span>
          </label>
          <select
            {...register("reason")}
            className="w-full px-4 py-2 border rounded-md"
          >
            <option value="">Select a reason...</option>
            <option value="DEFECTIVE">Defective Product</option>
            <option value="WRONG_ITEM">Wrong Item Received</option>
            <option value="DAMAGED">Damaged in Shipping</option>
            <option value="NOT_AS_DESCRIBED">Not as Described</option>
            <option value="SIZE_ISSUE">Size/Size Issue</option>
            <option value="OTHER">Other</option>
          </select>
          {errors.reason && (
            <p className="text-sm text-destructive mt-1">
              {errors.reason.message}
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Additional Notes (optional)
          </label>
          <textarea
            {...register("notes")}
            rows={4}
            className="w-full px-4 py-2 border rounded-md"
            placeholder="Please provide any additional details..."
          />
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
            {isSubmitting ? "Submitting..." : "Submit Return Request"}
          </button>
        </div>
      </form>
    </div>
  );
}

