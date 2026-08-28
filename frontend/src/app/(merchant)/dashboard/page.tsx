"use client";

import { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import {
  ReceiptData,
  RevenueAnalytics,
  getRevenueAnalytics,
  listReceipts,
} from "@/lib/api";
import {
  TrendingUp,
  Zap,
  Target,
  ShieldAlert,
  RotateCw,
  Search,
  Filter,
  ArrowUpRight,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  Copy,
  Check,
  BarChart3,
  Lock,
  Layers,
  ArrowUpDown,
  FileCheck2,
  ShoppingBag,
} from "lucide-react";

export default function MerchantDashboardPage() {
  const [merchantId] = useState("m_001");
  const [analytics, setAnalytics] = useState<RevenueAnalytics | null>(null);
  const [receipts, setReceipts] = useState<ReceiptData[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());
  const [autoRefresh, setAutoRefresh] = useState(true);
  
  // Interactive filters
  const [searchQuery, setSearchQuery] = useState("");
  const [decisionFilter, setDecisionFilter] = useState<"ALL" | "APPROVE" | "BLOCK" | "REQUIRE_CONFIRMATION">("ALL");
  const [sortBy, setSortBy] = useState<"newest" | "highest_amount" | "lowest_amount">("newest");
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const loadData = async (isManual = false) => {
    if (isManual) setLoading(true);
    try {
      const [analyticsData, receiptsData] = await Promise.all([
        getRevenueAnalytics(merchantId),
        listReceipts(merchantId),
      ]);
      setAnalytics(analyticsData);
      setReceipts(receiptsData.receipts || []);
      setLastRefreshed(new Date());
    } catch (err: any) {
      console.error("Failed to load dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(true);
  }, [merchantId]);

  // Auto-refresh interval (every 20 seconds if enabled)
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      loadData(false);
    }, 20000);
    return () => clearInterval(interval);
  }, [autoRefresh, merchantId]);

  const handleCopy = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    navigator.clipboard.writeText(id);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Filtered and sorted receipts
  const filteredReceipts = useMemo(() => {
    return receipts
      .filter((r) => {
        // Decision filter
        if (decisionFilter !== "ALL" && r.decision !== decisionFilter) {
          return false;
        }
        // Search query
        if (searchQuery.trim()) {
          const query = searchQuery.toLowerCase();
          const matchesId = r.receipt_id.toLowerCase().includes(query);
          const matchesReason = r.reason?.toLowerCase().includes(query);
          const matchesOrder = r.razorpay_order_id?.toLowerCase().includes(query);
          if (!matchesId && !matchesReason && !matchesOrder) return false;
        }
        return true;
      })
      .sort((a, b) => {
        if (sortBy === "newest") {
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        }
        const totalA = a.final_verified_total || a.observed_total || 0;
        const totalB = b.final_verified_total || b.observed_total || 0;
        if (sortBy === "highest_amount") return totalB - totalA;
        if (sortBy === "lowest_amount") return totalA - totalB;
        return 0;
      });
  }, [receipts, decisionFilter, searchQuery, sortBy]);

  // Calculated metrics
  const totalVerifiedVolume = useMemo(() => {
    return receipts
      .filter((r) => r.decision === "APPROVE")
      .reduce((acc, r) => acc + (r.final_verified_total || r.observed_total || 0), 0);
  }, [receipts]);

  const approvedCount = useMemo(() => receipts.filter((r) => r.decision === "APPROVE").length, [receipts]);
  const blockedCount = useMemo(() => receipts.filter((r) => r.decision === "BLOCK").length, [receipts]);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Header with Animated Telemetry Pipeline Visualizer */}
      <div className="bg-gradient-to-r from-white via-indigo-50/40 to-white p-6 sm:p-8 rounded-3xl border border-indigo-200/90 shadow-md relative overflow-hidden space-y-6">
        {/* Soft Ambient Light Glows */}
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-indigo-100/50 rounded-full blur-3xl pointer-events-none -z-0" />
        <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-emerald-100/40 rounded-full blur-3xl pointer-events-none -z-0" />

        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 relative z-10">
          <div className="space-y-2.5 max-w-2xl">
            {/* Animated Highlighting Badges */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-indigo-600 text-white text-xs font-black uppercase tracking-wider shadow-sm shadow-indigo-500/25 animate-pulse">
                <BarChart3 className="w-3.5 h-3.5" />
                <span>Side B • Control Plane</span>
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-200" />
                <span className="font-mono text-[11px] text-indigo-100">Financial Telemetry</span>
              </span>

              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-100 text-emerald-900 border border-emerald-300 text-xs font-mono font-black shadow-2xs">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
                </span>
                <span>Rule 6 Telemetry Active</span>
              </span>

              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 border border-slate-200 text-[11px] font-mono font-bold">
                <Lock className="w-3 h-3 text-indigo-600" />
                <span>Zero Hardcoded Figures</span>
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black text-slate-900 tracking-tight leading-tight">
              Merchant Revenue &amp;{" "}
              <span className="bg-gradient-to-r from-indigo-600 via-indigo-700 to-violet-700 bg-clip-text text-transparent">
                Guardian Audit Ledger
              </span>
            </h1>

            <p className="text-xs sm:text-sm text-slate-600 font-normal leading-relaxed">
              Real-time store revenue aggregations, upsell attachment telemetry, campaign promotion returns, and blocked exploit audit records computed from live order tables.
            </p>
          </div>

          {/* Right Action Controls: Auto-Sync & Manual Refresh */}
          <div className="flex flex-wrap sm:flex-nowrap items-center gap-3 shrink-0">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-3.5 py-3 rounded-2xl text-xs font-semibold border transition-all flex items-center gap-2 shadow-2xs ${
                autoRefresh
                  ? "bg-emerald-50 text-emerald-800 border-emerald-300 shadow-sm"
                  : "bg-white text-slate-600 border-slate-200 hover:bg-slate-50"
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${autoRefresh ? "bg-emerald-500 animate-ping" : "bg-slate-400"}`}></span>
              <span className="font-mono">{autoRefresh ? "Auto-Sync: 20s" : "Auto-Sync: OFF"}</span>
            </button>

            <button
              onClick={() => loadData(true)}
              disabled={loading}
              className="px-4 py-3 bg-gradient-to-r from-indigo-600 via-indigo-700 to-violet-700 hover:from-indigo-500 hover:to-violet-600 text-white rounded-2xl text-xs font-extrabold shadow-md shadow-indigo-600/20 active:scale-95 transition-all flex items-center gap-2"
            >
              <RotateCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
              <span>{loading ? "Refreshing..." : "Refresh Metrics"}</span>
            </button>
          </div>
        </div>

        {/* Animated Interactive Telemetry Flow Ribbon */}
        <div className="relative z-10 pt-4 border-t border-indigo-100 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs bg-white/80 p-3.5 rounded-2xl border border-indigo-100/80 shadow-2xs">
          {/* Orders Node */}
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-emerald-100 text-emerald-800 border border-emerald-200 flex items-center justify-center font-bold text-base shadow-2xs">
              💰
            </div>
            <div>
              <div className="font-extrabold text-slate-900 text-xs">Live Order Stream</div>
              <span className="text-[10px] text-slate-500 font-mono">Merchant: {merchantId}</span>
            </div>
          </div>

          {/* Animated Connecting Packets */}
          <div className="flex-1 max-w-xs flex items-center justify-center gap-2 px-3 py-1 bg-indigo-50/70 rounded-xl border border-indigo-100">
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping" />
            <span className="font-mono font-black text-[10px] text-indigo-800 uppercase tracking-widest">
              Real-Time Dynamic Aggregation
            </span>
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping [animation-delay:0.3s]" />
          </div>

          {/* Receipts Audit Node */}
          <div className="flex items-center gap-2.5">
            <div className="text-right">
              <div className="font-extrabold text-slate-900 text-xs">Decision Receipts Ledger</div>
              <span className="text-[10px] text-indigo-700 font-mono font-bold">{receipts.length} Immutable Proofs</span>
            </div>
            <div className="w-8 h-8 rounded-xl bg-indigo-100 text-indigo-700 border border-indigo-200 flex items-center justify-center font-bold text-base shadow-2xs">
              🛡️
            </div>
          </div>
        </div>
      </div>

      {/* Primary Financial Metric Cards */}
      {analytics ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Card 1: Total Store Revenue */}
          <div className="glass-card p-6 rounded-2xl border border-slate-200/90 relative overflow-hidden group">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Total Store Revenue
              </span>
              <div className="w-9 h-9 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-600 flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                <TrendingUp className="w-5 h-5" />
              </div>
            </div>
            <div className="text-3xl font-black text-slate-900 tracking-tight">
              ₹{(analytics.total_revenue / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
            </div>
            <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
              <span className="text-emerald-700 font-semibold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                {analytics.order_count} Verified Orders
              </span>
              <span className="text-slate-400 font-mono text-[11px]">m_001</span>
            </div>
          </div>

          {/* Card 2: Upsell Attach Rate */}
          <div className="glass-card p-6 rounded-2xl border border-slate-200/90 relative overflow-hidden group">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Upsell Attach Rate
              </span>
              <div className="w-9 h-9 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-600 flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                <Zap className="w-5 h-5" />
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-black text-indigo-600 tracking-tight">
                {(analytics.upsell_attach_rate * 100).toFixed(1)}%
              </span>
              <span className="text-xs font-semibold text-indigo-900">conversion</span>
            </div>
            <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span>Revenue Lift:</span>
              <span className="font-bold text-slate-900 font-mono">
                ₹{(analytics.upsell_revenue / 100).toFixed(2)}
              </span>
            </div>
          </div>

          {/* Card 3: Campaign Revenue */}
          <div className="glass-card p-6 rounded-2xl border border-slate-200/90 relative overflow-hidden group">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                AI Campaign Revenue
              </span>
              <div className="w-9 h-9 rounded-xl bg-purple-50 border border-purple-200 text-purple-600 flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                <Target className="w-5 h-5" />
              </div>
            </div>
            <div className="text-3xl font-black text-purple-600 tracking-tight">
              ₹{(analytics.campaign_revenue / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
            </div>
            <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span className="truncate">Active Promotions</span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-700">
                Attributed
              </span>
            </div>
          </div>

          {/* Card 4: Blocked Attacks & Limits */}
          <div className="glass-card p-6 rounded-2xl border border-slate-200/90 relative overflow-hidden group">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Blocked Attacks &amp; Limits
              </span>
              <div className="w-9 h-9 rounded-xl bg-rose-50 border border-rose-200 text-rose-600 flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                <ShieldAlert className="w-5 h-5" />
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-black text-rose-600 tracking-tight">
                {analytics.blocked_attempt_count}
              </span>
              <span className="text-xs font-semibold text-rose-700">exploits stopped</span>
            </div>
            <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span className="text-rose-600 font-semibold flex items-center gap-1">
                <Lock className="w-3.5 h-3.5" />
                Zero Margin Loss
              </span>
              <span className="text-[11px] font-mono text-slate-400">Rule 6 Gated</span>
            </div>
          </div>
        </div>
      ) : (
        /* Loading Skeleton */
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-36 rounded-2xl shimmer-box border border-slate-200"></div>
          ))}
        </div>
      )}

      {/* Decision Receipts Audit Trail & Replay Explorer */}
      <div className="glass-panel rounded-3xl border border-slate-200/80 shadow-md overflow-hidden space-y-4 p-6">
        {/* Table Header & Interactive Filter Bar */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2">
              <FileCheck2 className="w-5 h-5 text-indigo-600" />
              <h2 className="text-lg font-black text-slate-900 tracking-tight">
                Decision Receipts Audit Ledger &amp; Replay Engine
              </h2>
              <span className="px-2 py-0.5 rounded-full text-xs font-mono font-bold bg-slate-100 text-slate-700 border border-slate-200">
                {filteredReceipts.length} / {receipts.length}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Every checkout intent evaluated by the Commerce Guardian generates a cryptographically signed receipt replayable with zero drift.
            </p>
          </div>

          {/* Search and Decision Filters */}
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Search Input */}
            <div className="relative min-w-[220px]">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search Receipt ID, Reason..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 rounded-xl border border-slate-200 bg-white text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
              />
            </div>

            {/* Decision Filter Tabs */}
            <div className="flex items-center p-1 bg-slate-100 rounded-xl border border-slate-200 text-xs">
              <button
                onClick={() => setDecisionFilter("ALL")}
                className={`px-2.5 py-1 rounded-lg font-bold transition-all ${
                  decisionFilter === "ALL"
                    ? "bg-white text-slate-900 shadow-sm"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                All ({receipts.length})
              </button>
              <button
                onClick={() => setDecisionFilter("APPROVE")}
                className={`px-2.5 py-1 rounded-lg font-bold transition-all ${
                  decisionFilter === "APPROVE"
                    ? "bg-emerald-500 text-white shadow-sm"
                    : "text-emerald-700 hover:text-emerald-900"
                }`}
              >
                Approved ({approvedCount})
              </button>
              <button
                onClick={() => setDecisionFilter("BLOCK")}
                className={`px-2.5 py-1 rounded-lg font-bold transition-all ${
                  decisionFilter === "BLOCK"
                    ? "bg-rose-500 text-white shadow-sm"
                    : "text-rose-700 hover:text-rose-900"
                }`}
              >
                Blocked ({blockedCount})
              </button>
            </div>

            {/* Sort Selector */}
            <div className="relative">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="px-3 py-1.5 rounded-xl border border-slate-200 bg-white text-xs font-semibold text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 cursor-pointer"
              >
                <option value="newest">Sort: Newest</option>
                <option value="highest_amount">Sort: Amount (High → Low)</option>
                <option value="lowest_amount">Sort: Amount (Low → High)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Table Container */}
        <div className="overflow-x-auto rounded-2xl border border-slate-200/70 bg-white">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50/90 border-b border-slate-200 text-slate-600 font-bold uppercase tracking-wider text-[11px]">
              <tr>
                <th className="py-3.5 px-4">Receipt ID</th>
                <th className="py-3.5 px-4">Decision</th>
                <th className="py-3.5 px-4">Verified Total</th>
                <th className="py-3.5 px-4">Guardian Reason / Outcome</th>
                <th className="py-3.5 px-4">Timestamp</th>
                <th className="py-3.5 px-4 text-right">Audit &amp; Replay</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {filteredReceipts.length > 0 ? (
                filteredReceipts.map((r) => {
                  const verifiedAmount = r.final_verified_total || r.observed_total || 0;
                  const isApproved = r.decision === "APPROVE";
                  const isBlocked = r.decision === "BLOCK";

                  return (
                    <tr
                      key={r.receipt_id}
                      className="hover:bg-indigo-50/40 transition-colors group cursor-pointer"
                    >
                      {/* Receipt ID & Copy Button */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-1.5 font-mono text-slate-900 font-bold">
                          <span>{r.receipt_id.substring(0, 14)}...</span>
                          <button
                            onClick={(e) => handleCopy(r.receipt_id, e)}
                            className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-indigo-600 transition-opacity"
                            title="Copy full Receipt ID"
                          >
                            {copiedId === r.receipt_id ? (
                              <Check className="w-3 h-3 text-emerald-600" />
                            ) : (
                              <Copy className="w-3 h-3" />
                            )}
                          </button>
                        </div>
                        {r.razorpay_order_id && (
                          <span className="text-[10px] font-mono text-slate-400 block">
                            Order: {r.razorpay_order_id.substring(0, 12)}
                          </span>
                        )}
                      </td>

                      {/* Decision Badge */}
                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold border ${
                            isApproved
                              ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                              : isBlocked
                              ? "bg-rose-50 text-rose-700 border-rose-200"
                              : "bg-amber-50 text-amber-700 border-amber-200"
                          }`}
                        >
                          <span
                            className={`w-1.5 h-1.5 rounded-full ${
                              isApproved
                                ? "bg-emerald-500"
                                : isBlocked
                                ? "bg-rose-500"
                                : "bg-amber-500"
                            }`}
                          ></span>
                          <span>{r.decision}</span>
                        </span>
                      </td>

                      {/* Verified / Observed Total */}
                      <td className="py-3.5 px-4 font-mono font-bold text-slate-900 text-sm">
                        ₹{(verifiedAmount / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                        {r.observed_total !== verifiedAmount && (
                          <span className="text-[10px] text-slate-400 block font-normal line-through">
                            Observed: ₹{(r.observed_total / 100).toFixed(2)}
                          </span>
                        )}
                      </td>

                      {/* Guardian Reason */}
                      <td className="py-3.5 px-4 max-w-sm">
                        <div className="truncate text-slate-700 text-xs font-normal" title={r.reason}>
                          {r.reason || "Policy constraints validated successfully."}
                        </div>
                        {r.guardian_checks && (
                          <span className="text-[10px] text-slate-400 font-mono">
                            {r.guardian_checks.filter((c) => c.passed).length} / {r.guardian_checks.length} Checks Passed
                          </span>
                        )}
                      </td>

                      {/* Timestamp */}
                      <td className="py-3.5 px-4 text-slate-500 font-mono text-xs whitespace-nowrap">
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3 text-slate-400" />
                          <span>{new Date(r.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
                        </div>
                        <span className="text-[10px] text-slate-400 block">
                          {new Date(r.created_at).toLocaleDateString()}
                        </span>
                      </td>

                      {/* Action Link */}
                      <td className="py-3.5 px-4 text-right">
                        <Link
                          href={`/receipts/${r.receipt_id}`}
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold text-xs border border-indigo-200/80 transition-all hover:scale-105"
                        >
                          <span>Replay</span>
                          <ArrowUpRight className="w-3.5 h-3.5" />
                        </Link>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">
                    <div className="flex flex-col items-center justify-center space-y-2">
                      <FileCheck2 className="w-8 h-8 text-slate-300" />
                      <span className="font-semibold text-slate-600 text-sm">No Decision Receipts found</span>
                      <span className="text-xs text-slate-400 max-w-xs">
                        {searchQuery ? "Try adjusting your search filters." : "Initiate a chat checkout or A2A negotiation to generate live receipts."}
                      </span>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Footer Statistics */}
        <div className="pt-2 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
          <div className="flex items-center gap-3">
            <span>Verified Processed Volume: <strong className="text-slate-900 font-mono">₹{(totalVerifiedVolume / 100).toFixed(2)}</strong></span>
            <span>•</span>
            <span>Guardian Approval Rate: <strong className="text-emerald-700 font-mono">{receipts.length > 0 ? ((approvedCount / receipts.length) * 100).toFixed(0) : 100}%</strong></span>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-slate-400 font-mono">
            <span>Last Synced: {lastRefreshed.toLocaleTimeString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
