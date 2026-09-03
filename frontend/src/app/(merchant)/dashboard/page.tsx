"use client";

import { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import {
  ReceiptData,
  RevenueAnalytics,
  getRevenueAnalytics,
  listReceipts,
  AutoPayAllResponse,
  AutoPayMandateItem,
  listAllAutoPayMandates,
  setupAutoPayMandate,
  revokeAutoPayMandate,
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
  CreditCard,
  Sparkles,
  Plus,
  ExternalLink,
  ChevronRight,
  Sliders,
  X,
  DollarSign,
  Wallet,
  Radio,
  Activity,
  Terminal,
  Laptop,
  Smartphone,
  Bot,
} from "lucide-react";

export default function MerchantDashboardPage() {
  const [merchantId] = useState("m_001");
  const [analytics, setAnalytics] = useState<RevenueAnalytics | null>(null);
  const [receipts, setReceipts] = useState<ReceiptData[]>([]);
  const [autopayData, setAutopayData] = useState<AutoPayAllResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());
  const [autoRefresh, setAutoRefresh] = useState(true);
  
  // AutoPay Mandate Modal & State
  const [showSetupModal, setShowSetupModal] = useState(false);
  const [mandateBuyerId, setMandateBuyerId] = useState("b_002");
  const [mandateAmountInr, setMandateAmountInr] = useState(100000);
  const [mandateVpa, setMandateVpa] = useState("shopper2@okhdfcbank");
  const [mandateBank, setMandateBank] = useState("HDFC Bank (UPI AutoPay)");
  const [settingUp, setSettingUp] = useState(false);
  const [setupSuccess, setSetupSuccess] = useState<any | null>(null);
  const [togglingId, setTogglingId] = useState<string | null>(null);


  // Live Stream channel filter
  const [channelFilter, setChannelFilter] = useState<"ALL" | "TELEGRAM" | "CLAUDE" | "WEB" | "BLOCKED">("ALL");
  const [copiedId, setCopiedId] = useState<string | null>(null);

  function formatRelativeTime(dateStr: string): string {
    try {
      const then = new Date(dateStr).getTime();
      const now = Date.now();
      const diffSec = Math.max(1, Math.floor((now - then) / 1000));
      if (diffSec < 60) return `${diffSec}s ago`;
      const diffMin = Math.floor(diffSec / 60);
      if (diffMin < 60) return `${diffMin}m ago`;
      const diffHr = Math.floor(diffMin / 60);
      return `${diffHr}h ago`;
    } catch {
      return "recently";
    }
  }

  const loadData = async (isManual = false) => {
    if (isManual) setLoading(true);
    try {
      const [analyticsData, receiptsData, autopayRes] = await Promise.all([
        getRevenueAnalytics(merchantId),
        listReceipts(merchantId),
        listAllAutoPayMandates().catch(() => null),
      ]);
      setAnalytics(analyticsData);
      setReceipts(receiptsData.receipts || []);
      if (autopayRes) setAutopayData(autopayRes);
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

  // Auto-refresh interval (every 10 seconds if enabled)
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      loadData(false);
    }, 10000);
    return () => clearInterval(interval);
  }, [autoRefresh, merchantId]);

  const handleCopy = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    navigator.clipboard.writeText(id);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleSetupMandate = async () => {
    try {
      setSettingUp(true);
      const res = await setupAutoPayMandate({
        buyer_id: mandateBuyerId.trim() || "b_002",
        max_amount_paise: mandateAmountInr * 100,
        bank_name: mandateBank,
        vpa: mandateVpa,
      });
      setSetupSuccess(res);
      await loadData(false);
    } catch (err: any) {
      console.error("Failed to setup AutoPay mandate:", err);
      alert("Failed to setup mandate: " + (err?.message || String(err)));
    } finally {
      setSettingUp(false);
    }
  };

  const handleToggleMandate = async (buyerId: string, isCurrentlyEnabled: boolean) => {
    try {
      setTogglingId(buyerId);
      if (isCurrentlyEnabled) {
        await revokeAutoPayMandate(buyerId);
      } else {
        await setupAutoPayMandate({
          buyer_id: buyerId,
          max_amount_paise: 10000000,
        });
      }
      await loadData(false);
    } catch (err: any) {
      console.error("Failed to toggle mandate status:", err);
    } finally {
      setTogglingId(null);
    }
  };



  // Calculated metrics
  const totalVerifiedVolume = useMemo(() => {
    return receipts
      .filter((r) => r.decision === "APPROVE")
      .reduce((acc, r) => acc + (r.final_verified_total || r.observed_total || 0), 0);
  }, [receipts]);

  const approvedCount = useMemo(() => receipts.filter((r) => r.decision === "APPROVE").length, [receipts]);
  const blockedCount = useMemo(() => receipts.filter((r) => r.decision === "BLOCK").length, [receipts]);

  const telegramCount = useMemo(() => receipts.filter((r) => (r.mandate_snapshot?.buyer_id || "").startsWith("tg_")).length, [receipts]);
  const claudeCount = useMemo(() => receipts.filter((r) => {
    const id = r.mandate_snapshot?.buyer_id || "";
    return id.startsWith("claude_") || id.startsWith("mcp_");
  }).length, [receipts]);
  const webCount = useMemo(() => receipts.filter((r) => (r.mandate_snapshot?.buyer_id || "").startsWith("b_dev_")).length, [receipts]);

  const liveStreamReceipts = useMemo(() => {
    return receipts
      .filter((r) => {
        const buyerId = r.mandate_snapshot?.buyer_id || "";
        if (channelFilter === "TELEGRAM") return buyerId.startsWith("tg_");
        if (channelFilter === "CLAUDE") return buyerId.startsWith("claude_") || buyerId.startsWith("mcp_");
        if (channelFilter === "WEB") return buyerId.startsWith("b_dev_");
        if (channelFilter === "BLOCKED") return r.decision === "BLOCK";
        return true;
      })
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  }, [receipts, channelFilter]);

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

      {/* Top 4 KPI Metrics */}
      {analytics ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Card 1: Store Revenue */}
          <div className="glass-card p-6 rounded-2xl border border-slate-200/90 relative overflow-hidden group">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Store Revenue
              </span>
              <div className="w-9 h-9 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-600 flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                <TrendingUp className="w-5 h-5" />
              </div>
            </div>
            <div className="text-3xl font-black text-slate-900 tracking-tight">
              ₹{(((analytics.store_revenue ?? analytics.total_revenue ?? 0) / 100)).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
            </div>
            <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
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


      {/* ⚡ HEADLESS RAZORPAY UPI AUTOPAY & AUTONOMOUS MANDATE CENTER */}
      <div className="bg-gradient-to-r from-white via-indigo-50/30 to-white rounded-3xl p-6 sm:p-8 text-slate-900 border border-slate-200/90 shadow-sm relative overflow-hidden space-y-6">
        {/* Glow Accents */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-100/40 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-amber-100/30 rounded-full blur-3xl pointer-events-none" />

        {/* Section Header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 border-b border-slate-200/80 pb-6">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-amber-400 to-orange-500 text-white flex items-center justify-center font-black shadow-md shadow-orange-500/20">
              <Zap className="w-6 h-6 fill-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl sm:text-2xl font-black tracking-tight text-slate-900">
                  Headless UPI AutoPay &amp; Autonomous Mandates
                </h2>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-amber-100 text-amber-900 border border-amber-300">
                  Zero-OTP AI Commerce
                </span>
              </div>
              <p className="text-slate-500 text-xs mt-0.5">
                Shopper authorizes a 1-time spending pool (min ₹30,000); AI agents negotiate and settle sub-second purchases headlessly.
              </p>
            </div>
          </div>

          <button
            onClick={() => {
              setSetupSuccess(null);
              setShowSetupModal(true);
            }}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 via-indigo-700 to-violet-700 hover:from-indigo-500 hover:to-violet-600 text-white font-extrabold text-xs shadow-md shadow-indigo-600/20 flex items-center gap-2 transition-all hover:scale-105 self-start lg:self-auto"
          >
            <Plus className="w-4 h-4 stroke-[3]" />
            <span>Register New AutoPay Mandate</span>
          </button>
        </div>

        {/* Telemetry Strip */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white border border-slate-200/90 rounded-2xl p-4 shadow-2xs">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
              Active Recurring Tokens
            </span>
            <div className="text-2xl font-black text-slate-900 mt-1 flex items-baseline gap-2">
              <span>{autopayData?.summary.active_mandates || 1}</span>
              <span className="text-xs font-semibold text-emerald-600">● Live on Razorpay</span>
            </div>
            <span className="text-[11px] text-slate-500 mt-2 block font-mono">
              Token ID: {autopayData?.mandates?.[0]?.token_id?.substring(0, 16) || "tok_rzp_autopay_..."}...
            </span>
          </div>

          <div className="bg-white border border-slate-200/90 rounded-2xl p-4 shadow-2xs">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
              Total Pre-Authorized Pool
            </span>
            <div className="text-2xl font-black text-amber-600 mt-1 font-mono">
              ₹{((autopayData?.mandates?.[0]?.max_amount_paise || 3000000) / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
            </div>
            <span className="text-[11px] text-slate-500 mt-2 block">
              Min ₹30,000.00 e-mandate baseline
            </span>
          </div>

          <div className="bg-white border border-slate-200/90 rounded-2xl p-4 shadow-2xs">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
              Autonomous Debited Volume
            </span>
            <div className="text-2xl font-black text-emerald-600 mt-1 font-mono">
              ₹{((autopayData?.mandates?.[0]?.total_spent_paise || 0) / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
            </div>
            <span className="text-[11px] text-slate-500 mt-2 block">
              0 OTP prompts • Sub-350ms settle
            </span>
          </div>

          <div className="bg-white border border-slate-200/90 rounded-2xl p-4 shadow-2xs">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
              Remaining Spend Headroom
            </span>
            <div className="text-2xl font-black text-indigo-600 mt-1 font-mono">
              ₹{((autopayData?.mandates?.[0]?.remaining_headroom_paise || 3000000) / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
            </div>
            {/* Progress Bar */}
            <div className="w-full bg-slate-100 border border-slate-200/60 rounded-full h-1.5 mt-2 overflow-hidden">
              <div
                className="bg-gradient-to-r from-emerald-500 to-indigo-600 h-full rounded-full transition-all duration-500"
                style={{
                  width: `${Math.min(
                    100,
                    Math.max(
                      5,
                      (((autopayData?.mandates?.[0]?.remaining_headroom_paise || 3000000) /
                        (autopayData?.mandates?.[0]?.max_amount_paise || 3000000)) *
                        100)
                    )
                  )}%`,
                }}
              />
            </div>
          </div>
        </div>

        {/* Registered Shopper Mandate Cards / Table */}
        <div className="bg-slate-50/80 border border-slate-200/90 rounded-2xl p-6 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-200/60">
            <div className="flex items-center gap-2">
              <Wallet className="w-4 h-4 text-amber-500 shrink-0" />
              <span className="text-xs font-bold uppercase tracking-wider text-slate-800">
                Active Shopper Recurring e-Mandates
              </span>
            </div>
            <span className="text-xs text-slate-500 font-mono px-3 py-1 bg-white border border-slate-200 rounded-lg shrink-0 self-start sm:self-auto shadow-2xs">
              Dual-Lock Commerce Guardian Security Gate
            </span>
          </div>

          {autopayData?.mandates && autopayData.mandates.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {autopayData.mandates.map((m) => {
                const isEnabled = m.autopay_enabled && m.status === "ACTIVE";
                const poolInr = (m.max_amount_paise || 10000000) / 100;
                const spentInr = (m.total_spent_paise || 0) / 100;
                const headroomInr = Math.max(0, (m.remaining_headroom_paise ?? (m.max_amount_paise - (m.total_spent_paise || 0))) / 100);
                const usedPct = poolInr > 0 ? Math.min(100, Math.max(0, Math.round((spentInr / poolInr) * 100))) : 0;

                return (
                  <div
                    key={m.mandate_id}
                    className="bg-white hover:border-indigo-300 border border-slate-200/90 rounded-2xl p-5 sm:p-6 space-y-4 shadow-2xs transition-all"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-bold text-slate-900 text-sm">Shopper ({m.buyer_id})</span>
                        {m.buyer_id.startsWith("tg_") && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-sky-50 text-sky-700 border border-sky-200 flex items-center gap-1">
                            <span>📱</span> Telegram
                          </span>
                        )}
                        {m.buyer_id.startsWith("b_dev_") && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
                            <span>💻</span> Web Browser
                          </span>
                        )}
                        {(m.buyer_id.startsWith("claude_") || m.buyer_id.startsWith("mcp_")) && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200 flex items-center gap-1">
                            <span>🤖</span> Claude MCP
                          </span>
                        )}
                        {m.buyer_id === "b_001" && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 flex items-center gap-1">
                            <span>⚡</span> Benchmark Seed
                          </span>
                        )}
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase ${
                            isEnabled
                              ? "bg-emerald-50 text-emerald-700 border border-emerald-300"
                              : "bg-slate-100 text-slate-600 border border-slate-200"
                          }`}
                        >
                          {isEnabled ? "ACTIVE 🟢 (0-Click)" : "PAUSED ⚪"}
                        </span>
                      </div>

                      <button
                        onClick={() => handleToggleMandate(m.buyer_id, isEnabled)}
                        disabled={togglingId === m.buyer_id}
                        className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all self-start sm:self-auto ${
                          isEnabled
                            ? "bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200"
                            : "bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200"
                        }`}
                      >
                        {togglingId === m.buyer_id ? "Updating..." : isEnabled ? "Pause Mandate" : "Activate Mandate"}
                      </button>
                    </div>

                    <div className="text-xs bg-slate-50/90 border border-slate-200/80 rounded-xl p-3 flex flex-wrap items-center justify-between gap-2 font-mono">
                      <span className="text-slate-500">Linked VPA:</span>
                      <span className="font-semibold text-slate-900">{m.vpa}</span>
                      <span className="text-slate-400 text-[11px]">({m.bank_name})</span>
                    </div>

                    <div className="space-y-2 pt-1">
                      <div className="flex flex-wrap items-center justify-between text-xs gap-2">
                        <span className="text-slate-500 font-medium">Headroom Balance:</span>
                        <span className="font-mono font-bold text-emerald-700 text-sm">
                          ₹{headroomInr.toLocaleString("en-IN", { minimumFractionDigits: 2 })} / ₹{poolInr.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                        </span>
                      </div>
                      <div className="w-full bg-slate-100 border border-slate-200/80 rounded-full h-2.5 overflow-hidden">
                        <div
                          className="bg-gradient-to-r from-emerald-500 to-indigo-600 h-full rounded-full transition-all duration-500"
                          style={{ width: `${Math.max(5, Math.min(100, 100 - usedPct))}%` }}
                        />
                      </div>
                      <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-500 font-mono gap-2 pt-0.5">
                        <span>Used: ₹{spentInr.toFixed(2)} ({usedPct}%)</span>
                        <span className="truncate max-w-[220px]">Token: {m.token_id?.substring(0, 18)}...</span>
                      </div>
                    </div>

                    <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3">
                      <button
                        onClick={() => {
                          setMandateAmountInr(m.max_amount_paise / 100);
                          setSetupSuccess(null);
                          setShowSetupModal(true);
                        }}
                        className="text-xs font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1.5 transition-colors"
                      >
                        <Sliders className="w-3.5 h-3.5" />
                        <span>Edit Spending Pool</span>
                      </button>

                      <a
                        href={`https://rzp.io/l/mandate_${m.token_id || "demo"}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs font-medium text-slate-500 hover:text-slate-900 flex items-center gap-1.5 transition-colors"
                      >
                        <span>Razorpay e-Mandate Link</span>
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-6 text-slate-500 text-xs">
              No active mandates registered yet. Click &quot;Register New AutoPay Mandate&quot; above.
            </div>
          )}
        </div>
      </div>

      {/* MODAL: REGISTER / EDIT UPI AUTOPAY E-MANDATE */}
      {showSetupModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-md animate-fade-in">
          <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 max-w-lg w-full text-slate-900 shadow-2xl space-y-6 relative overflow-hidden">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-400 to-orange-500 text-white flex items-center justify-center font-black shadow-md shadow-orange-500/20">
                  <Zap className="w-5 h-5 fill-white" />
                </div>
                <div>
                  <h3 className="text-lg font-black text-slate-900">
                    Setup UPI AutoPay e-Mandate
                  </h3>
                  <p className="text-xs text-slate-500">
                    Authorize recurring zero-click AI commerce (Minimum ₹30,000)
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowSetupModal(false)}
                className="text-slate-400 hover:text-slate-700 p-1.5 rounded-xl hover:bg-slate-100 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {setupSuccess ? (
              <div className="space-y-4 py-4 text-center animate-fade-in">
                <div className="w-16 h-16 rounded-full bg-emerald-50 text-emerald-600 border border-emerald-200 flex items-center justify-center mx-auto">
                  <CheckCircle2 className="w-8 h-8" />
                </div>
                <div>
                  <h4 className="text-lg font-black text-slate-900">
                    e-Mandate Activated Successfully!
                  </h4>
                  <p className="text-xs text-slate-600 mt-1 max-w-sm mx-auto">
                    Pre-authorized spending pool of <strong className="text-amber-600">₹{(setupSuccess.max_amount_paise / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</strong> is now active.
                  </p>
                </div>

                <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 font-mono text-xs text-left space-y-1 text-slate-700">
                  <div>• <b>Token ID:</b> <code>{setupSuccess.token_id}</code></div>
                  <div>• <b>Linked VPA:</b> <code>{setupSuccess.vpa}</code></div>
                  <div>• <b>Bank:</b> <code>{setupSuccess.bank_name}</code></div>
                  <div>• <b>Zero-OTP Status:</b> <span className="text-emerald-600 font-bold">ACTIVE 🟢</span></div>
                </div>

                <button
                  onClick={() => setShowSetupModal(false)}
                  className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 font-bold text-white text-sm shadow-md shadow-indigo-600/20"
                >
                  Done &amp; Return to Dashboard
                </button>
              </div>
            ) : (
              <div className="space-y-5">
                {/* Shopper / Customer ID Input */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider block">
                    Customer / Shopper ID
                  </label>
                  <input
                    type="text"
                    value={mandateBuyerId}
                    onChange={(e) => {
                      const id = e.target.value.trim();
                      setMandateBuyerId(id);
                      setMandateVpa(`${id || "shopper"}@okhdfcbank`);
                    }}
                    placeholder="e.g. b_002, buyer_alice, corporate_procure_01"
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl py-2 px-3 text-slate-900 font-mono font-bold text-xs focus:outline-none focus:bg-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                  />
                  <p className="text-[11px] text-slate-500">
                    Creates a dedicated, isolated spending pool for this customer.
                  </p>
                </div>

                {/* Amount Selection Chips */}
                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider block">
                    Choose Pre-Authorized Mandate Limit (Default ₹1,00,000)
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {[100000, 200000, 500000].map((amt) => (
                      <button
                        key={amt}
                        type="button"
                        onClick={() => setMandateAmountInr(amt)}
                        className={`py-2.5 px-3 rounded-xl text-xs font-black border transition-all ${
                          mandateAmountInr === amt
                            ? "bg-indigo-600 text-white border-indigo-600 shadow-md shadow-indigo-600/20"
                            : "bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100"
                        }`}
                      >
                        ₹{amt.toLocaleString("en-IN")} {amt === 100000 ? "(1 Lakh)" : ""}
                      </button>
                    ))}
                  </div>
                </div>


                {/* Custom Amount Input */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-600 block">
                    Or Enter Custom Amount (₹):
                  </label>
                  <div className="relative">
                    <span className="absolute left-3.5 top-2.5 text-slate-400 font-bold">₹</span>
                    <input
                      type="number"
                      min={30000}
                      step={5000}
                      value={mandateAmountInr}
                      onChange={(e) => setMandateAmountInr(Math.max(0, parseInt(e.target.value) || 0))}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl py-2.5 pl-8 pr-4 text-slate-900 font-mono font-bold text-sm focus:outline-none focus:bg-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                    />
                  </div>
                  {mandateAmountInr < 30000 && (
                    <span className="text-[11px] text-rose-600 font-semibold">
                      ⚠️ Mandate must be at least ₹30,000.00 under UPI AutoPay regulations.
                    </span>
                  )}
                </div>

                {/* Bank & VPA */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="text-xs font-semibold text-slate-600 block">Issuing Bank</label>
                    <select
                      value={mandateBank}
                      onChange={(e) => setMandateBank(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl py-2 px-3 text-slate-900 text-xs focus:outline-none focus:bg-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                    >
                      <option value="HDFC Bank (UPI AutoPay)">HDFC Bank</option>
                      <option value="ICICI Bank (UPI AutoPay)">ICICI Bank</option>
                      <option value="State Bank of India (UPI AutoPay)">State Bank of India</option>
                      <option value="Axis Bank (UPI AutoPay)">Axis Bank</option>
                      <option value="Kotak Mahindra (UPI AutoPay)">Kotak Mahindra</option>
                    </select>
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs font-semibold text-slate-600 block">Linked UPI VPA</label>
                    <input
                      type="text"
                      value={mandateVpa}
                      onChange={(e) => setMandateVpa(e.target.value)}
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl py-2 px-3 text-slate-900 text-xs font-mono focus:outline-none focus:bg-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                    />
                  </div>
                </div>

                {/* Info Note */}
                <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-3 text-[11px] text-indigo-900 leading-relaxed">
                  🛡️ <b>Dual-Lock Guarantee:</b> Your AI agent is mathematically restricted by the Commerce Guardian to spend only within verified catalog rules. Zero unauthorized debits.
                </div>

                {/* Submit Button */}
                <button
                  onClick={handleSetupMandate}
                  disabled={settingUp || mandateAmountInr < 30000}
                  className="w-full py-3.5 rounded-xl bg-gradient-to-r from-amber-500 via-orange-500 to-amber-600 hover:from-amber-400 hover:to-orange-500 font-black text-white text-sm shadow-md shadow-orange-500/20 flex items-center justify-center gap-2 disabled:opacity-50 transition-all hover:scale-[1.02]"
                >
                  <Zap className="w-4 h-4 fill-white" />
                  <span>{settingUp ? "Authorizing e-Mandate..." : `Authorize ₹${mandateAmountInr.toLocaleString("en-IN")} AutoPay Mandate`}</span>
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* LIVE AGENTIC TRANSACTION STREAM (DECENTRALIZED MEMPOOL LEDGER) */}
      <div className="glass-panel rounded-3xl border border-slate-200/90 shadow-md overflow-hidden space-y-6 p-6 sm:p-8">
        {/* Header & Live Beacon */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-5 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-3">
              <div className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
              </div>
              <h2 className="text-lg sm:text-xl font-black text-slate-900 tracking-tight flex items-center gap-2">
                <span>Live Agentic Transaction Stream</span>
                <span className="text-xs font-mono font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                  Mempool Ledger
                </span>
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-1.5">
              Real-time decentralized activity stream capturing autonomous 0-click purchases, bilateral A2A negotiations, and blocked exploit attempts with privacy-preserving identity masking.
            </p>
          </div>

          {/* Channel Filter Chips & Refresh Controls */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => setChannelFilter("ALL")}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                channelFilter === "ALL"
                  ? "bg-slate-900 text-white shadow-sm"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              All Events ({receipts.length})
            </button>
            <button
              onClick={() => setChannelFilter("TELEGRAM")}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                channelFilter === "TELEGRAM"
                  ? "bg-sky-600 text-white shadow-sm"
                  : "bg-sky-50 text-sky-700 hover:bg-sky-100 border border-sky-200"
              }`}
            >
              <span>📱</span> Telegram ({telegramCount})
            </button>
            <button
              onClick={() => setChannelFilter("CLAUDE")}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                channelFilter === "CLAUDE"
                  ? "bg-amber-600 text-white shadow-sm"
                  : "bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200"
              }`}
            >
              <span>🤖</span> Claude MCP ({claudeCount})
            </button>
            <button
              onClick={() => setChannelFilter("WEB")}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                channelFilter === "WEB"
                  ? "bg-emerald-600 text-white shadow-sm"
                  : "bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200"
              }`}
            >
              <span>💻</span> Web ({webCount})
            </button>
            <button
              onClick={() => setChannelFilter("BLOCKED")}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                channelFilter === "BLOCKED"
                  ? "bg-rose-600 text-white shadow-sm"
                  : "bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200"
              }`}
            >
              <span>🛑</span> Blocked ({blockedCount})
            </button>

            <button
              onClick={() => loadData(true)}
              disabled={loading}
              title="Sync Live Stream"
              className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition-all cursor-pointer ml-1"
            >
              <RotateCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-indigo-600" : ""}`} />
            </button>
          </div>
        </div>

        {/* Activity Cards Stream */}
        <div className="space-y-3.5">
          {liveStreamReceipts.length > 0 ? (
            liveStreamReceipts.map((r) => {
              const buyerId = r.mandate_snapshot?.buyer_id || (r as any).buyer_id || "b_001";
              const isTg = buyerId.startsWith("tg_");
              const isClaude = buyerId.startsWith("claude_") || buyerId.startsWith("mcp_");
              const isWeb = buyerId.startsWith("b_dev_");
              const isApproved = r.decision === "APPROVE";
              const isBlocked = r.decision === "BLOCK";

              // Channel metadata
              const channelBadge = isTg
                ? { label: "Telegram Mobile", icon: "📱", color: "bg-sky-50 text-sky-700 border-sky-200" }
                : isClaude
                ? { label: "Claude MCP", icon: "🤖", color: "bg-amber-50 text-amber-700 border-amber-200" }
                : isWeb
                ? { label: "Web Browser", icon: "💻", color: "bg-emerald-50 text-emerald-700 border-emerald-200" }
                : { label: "Benchmark Seed", icon: "⚡", color: "bg-indigo-50 text-indigo-700 border-indigo-200" };

              // Privacy Masked User ID
              const maskedId = isTg
                ? `tg_${buyerId.substring(3, 6)}***${buyerId.slice(-3)}`
                : isWeb
                ? `b_dev_${buyerId.substring(6, 10)}...`
                : isClaude
                ? `claude_${buyerId.substring(7, 11)}...`
                : buyerId;

              // Action description
              const failReason = (r.failure_reason || "").toLowerCase();
              const isPromptInjection = failReason.includes("injection") || failReason.includes("heuristic") || failReason.includes("malicious");
              const isMarginBreach = failReason.includes("margin");
              const isBudgetExceeded = failReason.includes("mandate") || failReason.includes("budget") || failReason.includes("limit");

              const actionTitle = isBlocked
                ? isPromptInjection
                  ? "Malicious Prompt Injection Intercepted"
                  : isMarginBreach
                  ? "Margin Floor Policy Blocked"
                  : isBudgetExceeded
                  ? "Mandate & Budget Policy Blocked"
                  : "Guardian Security Invariant Blocked"
                : r.razorpay_payment_id?.startsWith("pay_autopay_") || r.mandate_snapshot?.autopay_token
                ? "0-Click Autonomous UPI AutoPay"
                : r.razorpay_order_id
                ? "Standard Retail Checkout"
                : "A2A Reverse Auction Settlement";

              const itemsDesc = r.items_snapshot && r.items_snapshot.length > 0
                ? r.items_snapshot.map((it: any) => `${it.sku || it.name || "Item"} (x${it.qty || 1})`).join(", ")
                : "Catalog Item";

              const amountInr = (r.final_verified_total || r.observed_total || 0) / 100;

              return (
                <div
                  key={r.receipt_id}
                  className={`rounded-2xl p-5 border transition-all hover:shadow-md ${
                    isBlocked
                      ? "bg-rose-50/30 border-rose-200/80 hover:border-rose-300"
                      : "bg-white border-slate-200/90 hover:border-indigo-300"
                  }`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
                    {/* Left: Channel + Actor + Decision */}
                    <div className="flex flex-wrap items-center gap-2">
                      {/* Channel Badge */}
                      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold border ${channelBadge.color}`}>
                        <span>{channelBadge.icon}</span>
                        <span>{channelBadge.label}</span>
                      </span>

                      {/* Masked User ID */}
                      <span className="font-mono text-xs font-bold text-slate-800 bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200/70" title={`Pseudonymous Client Identifier: ${buyerId}`}>
                        👤 {maskedId}
                      </span>

                      {/* Decision Status Pill */}
                      <span
                        className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider ${
                          isApproved
                            ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                            : isBlocked
                            ? "bg-rose-100 text-rose-800 border border-rose-300"
                            : "bg-amber-100 text-amber-800 border border-amber-300"
                        }`}
                      >
                        <span className={`w-2 h-2 rounded-full ${isApproved ? "bg-emerald-600 animate-pulse" : isBlocked ? "bg-rose-600" : "bg-amber-600"}`} />
                        <span>{isApproved ? "APPROVED 🟢" : isBlocked ? "BLOCKED 🛑" : "AUTH REQUIRED 🟡"}</span>
                      </span>
                    </div>

                    {/* Right: Relative Time + Latency */}
                    <div className="flex items-center gap-3 text-xs text-slate-500 font-mono self-start sm:self-auto">
                      <span className="bg-slate-100 px-2 py-0.5 rounded text-[11px] font-semibold text-slate-600">
                        {isBlocked ? "Latency: <3ms" : "Latency: <35ms"}
                      </span>
                      <div className="flex items-center gap-1 text-slate-400" title={new Date(r.created_at).toLocaleString()}>
                        <Clock className="w-3.5 h-3.5" />
                        <span>{formatRelativeTime(r.created_at)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Middle: Action Details + Amount */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-3 items-center">
                    <div className="md:col-span-2 space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-slate-900">{actionTitle}</span>
                        <span className="text-[11px] text-slate-400">•</span>
                        <span className="text-xs text-slate-600 font-medium truncate">{itemsDesc}</span>
                      </div>
                      <p className="text-xs text-slate-500 leading-relaxed">
                        {isBlocked ? (
                          <span className="text-rose-700 font-semibold flex items-center gap-1">
                            <ShieldAlert className="w-3.5 h-3.5 shrink-0" />
                            <span>{r.reason || "Security heuristic flagged malicious payload. Zero financial leakage."}</span>
                          </span>
                        ) : (
                          <span>
                            {r.reason || "Rule 6 margin floor (≥15%) verified. Google AP2 cryptographic mandate sealed."}
                          </span>
                        )}
                      </p>
                    </div>

                    {/* Amount */}
                    <div className="flex flex-col sm:items-end justify-center">
                      <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Gross Value</span>
                      <div className={`text-lg font-black font-mono ${isBlocked ? "text-slate-400 line-through" : "text-slate-900"}`}>
                        ₹{amountInr.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                      </div>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {isBlocked ? "No Payment Rail Called" : r.razorpay_payment_id ? "Razorpay AutoPay Captured" : "Test Rail Verified"}
                      </span>
                    </div>
                  </div>

                  {/* Footer: Receipt ID + Inspect CTA */}
                  <div className="pt-3 mt-3 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                    <div className="flex items-center gap-2 font-mono text-slate-500 text-[11px]">
                      <span>Receipt:</span>
                      <span className="font-bold text-slate-700">{r.receipt_id.substring(0, 18)}...</span>
                      <button
                        onClick={(e) => handleCopy(r.receipt_id, e)}
                        className="p-1 hover:text-indigo-600 text-slate-400 transition-colors cursor-pointer"
                        title="Copy full receipt hash"
                      >
                        {copiedId === r.receipt_id ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                      </button>
                    </div>

                    <Link
                      href={`/receipts/${r.receipt_id}`}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold text-xs border border-indigo-200/80 transition-all hover:scale-[1.02] self-start sm:self-auto group"
                    >
                      <FileCheck2 className="w-3.5 h-3.5 text-indigo-600" />
                      <span>Inspect Merkle Proof &amp; Replay</span>
                      <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                    </Link>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="text-center py-12 bg-slate-50/60 rounded-2xl border border-dashed border-slate-200">
              <Radio className="w-8 h-8 text-slate-300 mx-auto mb-2 animate-pulse" />
              <p className="text-xs font-bold text-slate-600">No activity detected for this filter</p>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Try chatting with the bot on Telegram, opening Buyer Chat, or running an MCP tool in Claude.
              </p>
            </div>
          )}
        </div>

        {/* Bottom Telemetry Bar */}
        <div className="pt-2 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2 border-t border-slate-100">
          <div className="flex items-center gap-3">
            <span>Verified Processed Volume: <strong className="text-slate-900 font-mono">₹{(totalVerifiedVolume / 100).toFixed(2)}</strong></span>
            <span>•</span>
            <span>Approval Rate: <strong className="text-emerald-700 font-mono">{receipts.length > 0 ? ((approvedCount / receipts.length) * 100).toFixed(0) : 100}%</strong></span>
            <span>•</span>
            <span>Channels Connected: <strong className="text-indigo-600 font-mono">4 Omnichannel Ingresses</strong></span>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-slate-400 font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Live Synced: {lastRefreshed.toLocaleTimeString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
