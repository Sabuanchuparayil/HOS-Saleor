"use client";

import { useQuery } from "@apollo/client/react";
import {
  GET_LOYALTY_BALANCE,
  GET_LOYALTY_TRANSACTIONS,
  GET_REWARDS,
} from "@/lib/graphql/queries";
import { Loader2, Star, Gift, ArrowDownUp } from "lucide-react";
import { formatDate } from "@/lib/utils";

export function RewardsPage() {
  const { data: balanceData, loading: balanceLoading } = useQuery(
    GET_LOYALTY_BALANCE,
    {
      fetchPolicy: "cache-and-network",
      errorPolicy: "ignore",
    }
  );

  const { data: rewardsData, loading: rewardsLoading } = useQuery(GET_REWARDS, {
    variables: { first: 50 },
    fetchPolicy: "cache-and-network",
    errorPolicy: "ignore",
  });

  const { data: txData, loading: txLoading } = useQuery(GET_LOYALTY_TRANSACTIONS, {
    variables: { first: 20 },
    fetchPolicy: "cache-and-network",
    errorPolicy: "ignore",
  });

  const balance = (balanceData as any)?.loyaltyPointsBalance?.balance ?? null;
  const rewards =
    (rewardsData as any)?.rewards?.edges?.map((e: any) => e.node).filter(Boolean) || [];
  const transactions =
    (txData as any)?.loyaltyPointsTransactions?.edges
      ?.map((e: any) => e.node)
      .filter(Boolean) || [];

  const loading = balanceLoading || rewardsLoading || txLoading;

  if (loading && balanceData == null && rewardsData == null && txData == null) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  // If the loyalty system isn't enabled on the backend, these fields won't exist.
  const loyaltyAvailable = balance !== null || rewards.length > 0 || transactions.length > 0;

  if (!loyaltyAvailable) {
    return (
      <div className="border rounded-lg p-8 text-center">
        <Star className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
        <h2 className="text-2xl font-bold mb-2">Loyalty is not enabled</h2>
        <p className="text-muted-foreground">
          Your backend doesn’t currently expose loyalty points/rewards APIs. If you enable the
          loyalty feature on Saleor, this page will automatically start showing your balance and
          rewards.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-10">
      <div className="p-6 bg-gradient-to-r from-primary/10 to-primary/5 border border-primary/20 rounded-lg">
        <div className="flex items-center gap-3 mb-2">
          <Star className="h-6 w-6 text-primary" />
          <h1 className="text-3xl font-bold">Loyalty & Rewards</h1>
        </div>
        <p className="text-muted-foreground">
          View your points, explore rewards, and track recent activity.
        </p>
        <div className="mt-6 flex items-baseline gap-3">
          <span className="text-sm text-muted-foreground">Available points</span>
          <span className="text-4xl font-bold text-primary">
            {balance === null ? "—" : Number(balance).toLocaleString()}
          </span>
        </div>
      </div>

      <section>
        <div className="flex items-center gap-2 mb-4">
          <Gift className="h-5 w-5 text-primary" />
          <h2 className="text-2xl font-bold">Available Rewards</h2>
        </div>

        {rewards.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {rewards.map((reward: any) => (
              <div key={reward.id} className="border rounded-lg p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="font-semibold text-lg mb-1">{reward.name}</h3>
                    {reward.description && (
                      <p className="text-sm text-muted-foreground">{reward.description}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-muted-foreground">Points</div>
                    <div className="text-xl font-bold text-primary">
                      {Number(reward.pointsRequired).toLocaleString()}
                    </div>
                  </div>
                </div>

                <div className="mt-4 text-sm text-muted-foreground">
                  Reward:{" "}
                  <span className="font-medium text-foreground">
                    {reward.discountType} {reward.discountValue}
                  </span>
                </div>

                <button
                  disabled={balance === null || Number(balance) < Number(reward.pointsRequired)}
                  className="mt-5 w-full inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-primary-foreground font-semibold hover:bg-primary/90 disabled:opacity-50"
                  title="Redemption requires backend mutation support"
                >
                  {balance !== null && Number(balance) >= Number(reward.pointsRequired)
                    ? "Redeem (coming soon)"
                    : "Not enough points"}
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="border rounded-lg p-8 text-center text-muted-foreground">
            No active rewards available right now.
          </div>
        )}
      </section>

      <section>
        <div className="flex items-center gap-2 mb-4">
          <ArrowDownUp className="h-5 w-5 text-primary" />
          <h2 className="text-2xl font-bold">Recent Activity</h2>
        </div>

        {transactions.length > 0 ? (
          <div className="border rounded-lg divide-y">
            {transactions.map((tx: any) => (
              <div key={tx.id} className="p-5 flex items-start justify-between gap-6">
                <div>
                  <div className="font-medium">
                    {tx.transactionType || "Transaction"}{" "}
                    <span className="text-muted-foreground">
                      · {tx.created ? formatDate(tx.created) : ""}
                    </span>
                  </div>
                  {tx.description && (
                    <div className="text-sm text-muted-foreground">{tx.description}</div>
                  )}
                  {tx.order?.number && (
                    <div className="text-sm text-muted-foreground">Order #{tx.order.number}</div>
                  )}
                </div>
                <div className="text-right">
                  <div className="text-sm text-muted-foreground">Points</div>
                  <div className="text-lg font-bold">{tx.points}</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="border rounded-lg p-8 text-center text-muted-foreground">
            No recent transactions.
          </div>
        )}
      </section>
    </div>
  );
}


