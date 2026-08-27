"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ReceiptData,
  RevenueAnalytics,
  getRevenueAnalytics,
  listReceipts,
} from "@/lib/api";

export default function MerchantDashboardPage() {
  const [merchantId] = useState("m_001");
  const [analytics, setAnalytics] = useState<RevenueAnalytics | null>(null);
  const [receipts, setReceipts] = useState<ReceiptData[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [analyticsData, receiptsData] = await Promise.all([
        getRevenueAnalytics(merchantId),
        listReceipts(merchantId),
      ]);
      setAnalytics(analyticsData);
      setReceipts(receiptsData.receipts || []);
    } catch (err: any) {
      console.error("Failed to load dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [merchantId]);

  return (
    <div className="space-y-8">
      {/* Dashboard Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900">Merchant Revenue & Control Plane</h1>
          <p className="text-sm text-slate-500">
            Real-time telemetry aggregated from live Order & Decision Receipt tables (Rule 6 compliant).
          </p>
        </div>
        <button
          onClick={loadData}
          disabled={loading}
          className="px-4 py-2 bg-white border border-slate-300 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
        >
          {loading ? "Refreshing..." : "🔄 Refresh Metrics"}
        </button>
      </div>

      {/* Metrics Grid */}
      {analytics && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <span className="text-xs font-semibold text-slate-500 block mb-1">Total Store Revenue</span>
            <span className="text-2xl font-extrabold text-slate-900">
              ₹{(analytics.total_revenue / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
            </span>
            <span className="text-[11px] text-emerald-600 font-medium block mt-1">
              Live from {analytics.order_count} paid orders
            </span>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <span className="text-xs font-semibold text-slate-500 block mb-1">Upsell Attach Rate</span>
            <span className="text-2xl font-extrabold text-indigo-600">
              {(analytics.upsell_attach_rate * 100).toFixed(0)}%
            </span>
            <span className="text-[11px] text-slate-500 block mt-1">
              ₹{(analytics.upsell_revenue / 100).toFixed(2)} upsell revenue
            </span>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <span className="text-xs font-semibold text-slate-500 block mb-1">Campaign Revenue</span>
            <span className="text-2xl font-extrabold text-emerald-600">
              ₹{(analytics.campaign_revenue / 100).toFixed(2)}
            </span>
            <span className="text-[11px] text-slate-500 block mt-1">
              Attributed to active AI promotions
            </span>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <span className="text-xs font-semibold text-slate-500 block mb-1">Blocked Attacks & Limits</span>
            <span className="text-2xl font-extrabold text-rose-600">
              {analytics.blocked_attempt_count}
            </span>
            <span className="text-[11px] text-slate-500 block mt-1">
              Audited in Decision Receipts
            </span>
          </div>
        </div>
      )}

      {/* Decision Receipts Audit Trail Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex justify-between items-center">
          <h2 className="text-base font-bold text-slate-900">Recent Decision Receipts & Audit Trail</h2>
          <span className="text-xs text-slate-500 font-mono">{receipts.length} total</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Receipt ID</th>
                <th className="py-3 px-4">Decision</th>
                <th className="py-3 px-4">Observed / Verified Total</th>
                <th className="py-3 px-4">Reason / Outcome</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {receipts.map((r) => (
                <tr key={r.receipt_id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3 px-4 font-mono text-slate-900 font-medium">{r.receipt_id.substring(0, 12)}...</td>
                  <td className="py-3 px-4">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        r.decision === "APPROVE"
                          ? "bg-emerald-100 text-emerald-800"
                          : r.decision === "BLOCK"
                          ? "bg-rose-100 text-rose-800"
                          : "bg-amber-100 text-amber-800"
                      }`}
                    >
                      {r.decision}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono">
                    ₹{((r.final_verified_total || r.observed_total) / 100).toFixed(2)}
                  </td>
                  <td className="py-3 px-4 max-w-xs truncate text-slate-600">{r.reason}</td>
                  <td className="py-3 px-4 text-slate-400 font-mono">
                    {new Date(r.created_at).toLocaleTimeString()}
                  </td>
                  <td className="py-3 px-4">
                    <Link
                      href={`/receipts/${r.receipt_id}`}
                      className="text-indigo-600 hover:underline font-semibold"
                    >
                      View & Replay &rarr;
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
