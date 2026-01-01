"use client";

import Link from "next/link";
import { Package, MapPin, CreditCard, Gift, Settings, LogOut, Star, Award } from "lucide-react";
import { useQuery } from "@apollo/client/react";
import { GET_USER_ORDERS, GET_LOYALTY_BALANCE, GET_USER_BADGES } from "@/lib/graphql/queries";

export function AccountDashboard() {
  const { data } = useQuery(GET_USER_ORDERS, {
    variables: { first: 5 },
    fetchPolicy: "cache-and-network",
    errorPolicy: "all", // Continue even if there are errors
  });

  const { data: loyaltyData } = useQuery(GET_LOYALTY_BALANCE, {
    fetchPolicy: "cache-and-network",
    errorPolicy: "ignore", // Ignore errors if loyalty system not available
    skip: false, // Try to fetch, but don't fail if it doesn't exist
  });

  const { data: badgesData } = useQuery(GET_USER_BADGES, {
    variables: { first: 5 },
    fetchPolicy: "cache-and-network",
    errorPolicy: "ignore", // Ignore errors if badges system not available
    skip: false, // Try to fetch, but don't fail if it doesn't exist
  });

  const recentOrders = (data as any)?.me?.orders?.edges?.map((edge: any) => edge.node) || [];
  const loyaltyBalance = (loyaltyData as any)?.loyaltyPointsBalance?.balance || 0;
  const userBadges = (badgesData as any)?.userBadges?.edges?.map((edge: any) => edge.node) || [];

  const menuItems = [
    {
      title: "Order History",
      description: "View and track your orders",
      icon: Package,
      href: "/account/orders",
      count: (data as any)?.me?.orders?.totalCount || 0,
    },
    {
      title: "Addresses",
      description: "Manage shipping addresses",
      icon: MapPin,
      href: "/account/addresses",
    },
    {
      title: "Payment Methods",
      description: "Manage saved payment methods",
      icon: CreditCard,
      href: "/account/payment-methods",
    },
    {
      title: "Returns",
      description: "Track return requests",
      icon: Gift,
      href: "/account/returns",
    },
    {
      title: "Loyalty & Rewards",
      description: "View points and redeem rewards",
      icon: Star,
      href: "/account/rewards",
    },
    {
      title: "Settings",
      description: "Account preferences",
      icon: Settings,
      href: "/account/settings",
    },
  ];

  return (
    <div>
      <h1 className="text-4xl font-bold mb-8">My Account</h1>

      {/* Loyalty Points Summary */}
      {(loyaltyBalance > 0 || userBadges.length > 0) && (
        <div className="mb-8 p-6 bg-gradient-to-r from-primary/10 to-primary/5 border border-primary/20 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold mb-2 flex items-center gap-2">
                <Star className="h-5 w-5 text-primary" />
                Loyalty Points
              </h2>
              <p className="text-3xl font-bold text-primary">{loyaltyBalance.toLocaleString()}</p>
              <p className="text-sm text-muted-foreground mt-1">Available points</p>
            </div>
            {userBadges.length > 0 && (
              <div className="text-right">
                <h3 className="text-sm font-medium mb-2 flex items-center gap-2 justify-end">
                  <Award className="h-4 w-4" />
                  Badges Earned
                </h3>
                <div className="flex gap-2 justify-end">
                  {userBadges.slice(0, 3).map((userBadge: any) => (
                    <div
                      key={userBadge.id}
                      className="px-3 py-1 bg-primary/20 text-primary rounded-full text-xs font-medium"
                      title={userBadge.badge?.name}
                    >
                      {userBadge.badge?.name || "Badge"}
                    </div>
                  ))}
                  {userBadges.length > 3 && (
                    <div className="px-3 py-1 bg-secondary text-secondary-foreground rounded-full text-xs">
                      +{userBadges.length - 3}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
          <Link
            href="/account/rewards"
            className="mt-4 inline-block text-sm text-primary hover:underline font-medium"
          >
            View rewards & redeem →
          </Link>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className="border rounded-lg p-6 hover:shadow-lg transition-shadow group"
            >
              <div className="flex items-start gap-4">
                <div className="p-3 bg-primary/10 rounded-lg group-hover:bg-primary/20 transition-colors">
                  <Icon className="h-6 w-6 text-primary" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="font-semibold text-lg group-hover:text-primary transition-colors">
                      {item.title}
                    </h3>
                    {item.count !== undefined && item.count > 0 && (
                      <span className="text-sm text-muted-foreground">({item.count})</span>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">{item.description}</p>
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      {recentOrders.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Recent Orders</h2>
            <Link
              href="/account/orders"
              className="text-primary hover:underline font-medium"
            >
              View All →
            </Link>
          </div>
          <div className="space-y-4">
            {recentOrders.map((order: any) => (
              <Link
                key={order.id}
                href={`/account/orders/${order.id}`}
                className="block border rounded-lg p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold mb-1">
                      Order #{order.number || order.id.slice(-8)}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(order.created).toLocaleDateString("en-US", {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold mb-1">
                      {order.total?.gross
                        ? new Intl.NumberFormat("en-US", {
                            style: "currency",
                            currency: order.total.gross.currency,
                          }).format(order.total.gross.amount)
                        : "N/A"}
                    </p>
                    <span
                      className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                        order.status === "FULFILLED"
                          ? "bg-green-100 text-green-800"
                          : order.status === "UNFULFILLED"
                          ? "bg-yellow-100 text-yellow-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {order.status || "Processing"}
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {recentOrders.length === 0 && (
        <div className="text-center py-12 border rounded-lg">
          <Package className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground mb-4">No orders yet</p>
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

