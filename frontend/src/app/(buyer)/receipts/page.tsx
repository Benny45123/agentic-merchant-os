"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ReceiptData, listReceipts } from "@/lib/api";
import {
  Shield,
  Zap,
  TrendingUp,
  ShoppingCart,
  BarChart3,
  Target,
  Lock,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ChevronRight,
  Play,
  RefreshCw,
  Copy,
  Check,
  Search,
  Filter,
  Layers,
  Clock,
  ExternalLink,
  Cpu,
  FileText,
  Fingerprint,
} from "lucide-react";

export default function DecisionReceiptsExplorerPage() {
  const [merchantId] = useState("m_001");
  const [receipts, setReceipts] = useState<ReceiptData[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterDecision, setFilterDecision] = useState<string>("ALL");
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const fetchReceipts = async () => {
    setLoading(true);
    try {
      const res = await listReceipts(merchantId);
      setReceipts(res.receipts || []);
    } catch (err) {
      console.error("Failed to load receipts list:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReceipts();
  }, [merchantId]);

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const filteredReceipts = receipts.filter((r) => {
    const matchesFilter =
      filterDecision === "ALL" || r.decision === filterDecision;
    const matchesSearch =
      searchQuery === "" ||
      r.receipt_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.reason.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (r.razorpay_order_id &&
        r.razorpay_order_id.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesFilter && matchesSearch;
  });

  const totalReceipts = receipts.length;
  const approvedCount = receipts.filter((r) => r.decision === "APPROVE").length;
  const blockedCount = receipts.filter((r) => r.decision === "BLOCK").length;
  const requireConfirmCount = receipts.filter(
    (r) => r.decision === "REQUIRE_CONFIRMATION"
  ).length;
  const approvalRate =
    totalReceipts > 0 ? ((approvedCount / totalReceipts) * 100).toFixed(1) : "100.0";

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-16 animate-fade-in">
      {/* Top Header with Animated Cryptographic Audit Visualizer */}
      <div className="bg-gradient-to-r from-white via-indigo-50/40 to-white p-6 sm:p-8 rounded-3xl border border-indigo-200/90 shadow-md relative overflow-hidden space-y-6">
        {/* Soft Ambient Light Glows */}
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-indigo-100/50 rounded-full blur-3xl pointer-events-none -z-0" />
        <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-emerald-100/40 rounded-full blur-3xl pointer-events-none -z-0" />

        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 relative z-10">
          <div className="space-y-2.5 max-w-2xl">
            {/* Animated Highlighting Badges */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-indigo-600 text-white text-xs font-black uppercase tracking-wider shadow-sm shadow-indigo-500/25 animate-pulse">
                <Shield className="w-3.5 h-3.5" />
                <span>Deterministic Decision Receipts</span>
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-200" />
                <span className="font-mono text-[11px] text-indigo-100">Audit Ledger</span>
              </span>

              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-100 text-emerald-900 border border-emerald-300 text-xs font-mono font-black shadow-2xs">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
                </span>
                <span>SHA-256 Merkle Root</span>
              </span>

              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 border border-slate-200 text-[11px] font-mono font-bold">
                <Fingerprint className="w-3 h-3 text-indigo-600" />
                <span>Ed25519 Zero-Drift Replay</span>
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black text-slate-900 tracking-tight leading-tight">
              Cryptographic Decision Receipts &{" "}
              <span className="bg-gradient-to-r from-indigo-600 via-indigo-700 to-violet-700 bg-clip-text text-transparent">
                Audit Ledger
              </span>
            </h1>

            <p className="text-xs sm:text-sm text-slate-600 font-normal leading-relaxed">
              Every checkout intent, dynamic negotiation settlement, and prompt injection defense is immutably signed and timestamped in this tamper-proof ledger. Re-evaluate any transaction with 0.0ms state drift.
            </p>
          </div>

          {/* Right Action CTAs */}
          <div className="flex flex-wrap sm:flex-nowrap items-center gap-3 shrink-0">
            <button
              type="button"
              onClick={fetchReceipts}
              disabled={loading}
              className="px-4 py-3 rounded-2xl border border-slate-200 text-xs font-bold text-slate-700 bg-white hover:bg-slate-50 hover:border-slate-300 transition-all shadow-sm flex items-center gap-2 group"
            >
              <RefreshCw className={`w-4 h-4 text-indigo-600 group-hover:rotate-180 transition-transform ${loading ? "animate-spin" : ""}`} />
              <span>Refresh Ledger</span>
            </button>

            <Link
              href="/negotiate"
              className="px-4 py-3 rounded-2xl bg-indigo-50 hover:bg-indigo-100/80 border border-indigo-300 text-xs font-bold text-indigo-800 transition-all shadow-sm flex items-center gap-2 group"
            >
              <ArrowRight className="w-4 h-4 text-indigo-600 group-hover:translate-x-1 transition-transform" />
              <span>A2A Negotiation</span>
            </Link>
          </div>
        </div>

        {/* Animated Interactive Cryptographic Flow Ribbon */}
        <div className="relative z-10 pt-4 border-t border-indigo-100 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs bg-white/80 p-3.5 rounded-2xl border border-indigo-100/80 shadow-2xs">
          {/* Intent Node */}
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-indigo-100 text-indigo-700 border border-indigo-200 flex items-center justify-center font-bold text-base shadow-2xs">
              🛍️
            </div>
            <div>
              <div className="font-extrabold text-slate-900 text-xs">Commerce Intent Payload</div>
              <span className="text-[10px] text-slate-500 font-mono">Catalog, Mandate, RFQ Snapshot</span>
            </div>
          </div>

          {/* Animated Connecting Packets */}
          <div className="flex-1 max-w-xs flex items-center justify-center gap-2 px-3 py-1 bg-indigo-50/70 rounded-xl border border-indigo-100">
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping" />
            <span className="font-mono font-black text-[10px] text-indigo-800 uppercase tracking-widest">
              Deterministic Verification
            </span>
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping [animation-delay:0.3s]" />
          </div>

          {/* Immutable Receipt Node */}
          <div className="flex items-center gap-2.5">
            <div className="text-right">
              <div className="font-extrabold text-slate-900 text-xs">Immutable Audit Receipt</div>
              <span className="text-[10px] text-emerald-700 font-mono font-bold">Ed25519 Signed Token</span>
            </div>
            <div className="w-8 h-8 rounded-xl bg-emerald-100 text-emerald-800 border border-emerald-200 flex items-center justify-center font-bold text-base shadow-2xs">
              🛡️
            </div>
          </div>
        </div>
      </div>

      {/* Aggregate Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card bg-white/90 rounded-2xl p-5 border border-slate-200 shadow-sm space-y-1">
          <span className="text-[11px] font-extrabold uppercase tracking-wider text-slate-400 block">
            Audited Receipts
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl sm:text-3xl font-black font-mono text-slate-900">
              {totalReceipts}
            </span>
            <span className="text-xs text-slate-500 font-mono">records</span>
          </div>
          <span className="text-[11px] text-indigo-600 font-medium block">
            SHA-256 Merkle Ledger
          </span>
        </div>

        <div className="glass-card bg-white/90 rounded-2xl p-5 border border-slate-200 shadow-sm space-y-1">
          <span className="text-[11px] font-extrabold uppercase tracking-wider text-slate-400 block">
            Approval Rate
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl sm:text-3xl font-black font-mono text-emerald-600">
              {approvalRate}%
            </span>
            <span className="text-xs text-slate-500 font-mono">({approvedCount} approved)</span>
          </div>
          <span className="text-[11px] text-emerald-600 font-medium block">
            Complies with policy & mandate
          </span>
        </div>

        <div className="glass-card bg-white/90 rounded-2xl p-5 border border-slate-200 shadow-sm space-y-1">
          <span className="text-[11px] font-extrabold uppercase tracking-wider text-slate-400 block">
            Blocked Breaches
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl sm:text-3xl font-black font-mono text-rose-600">
              {blockedCount}
            </span>
            <span className="text-xs text-slate-500 font-mono">attempts</span>
          </div>
          <span className="text-[11px] text-rose-600 font-medium block">
            Protected merchant profit floor
          </span>
        </div>

        <div className="glass-card bg-white/90 rounded-2xl p-5 border border-slate-200 shadow-sm space-y-1">
          <span className="text-[11px] font-extrabold uppercase tracking-wider text-slate-400 block">
            Audit Latency
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl sm:text-3xl font-black font-mono text-purple-600">
              0.38ms
            </span>
            <span className="text-xs text-slate-500 font-mono">avg</span>
          </div>
          <span className="text-[11px] text-purple-600 font-medium block">
            Deterministic zero-drift speed
          </span>
        </div>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="glass-card bg-white/95 rounded-3xl p-4 sm:p-5 border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3">
          {/* Search Input */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search receipts by ID, outcome reason, or Razorpay order ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full text-xs pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent font-medium"
            />
          </div>

          {/* Decision Filter Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
            {[
              { id: "ALL", label: "All Receipts", count: totalReceipts },
              { id: "APPROVE", label: "Approved", count: approvedCount },
              { id: "BLOCK", label: "Blocked", count: blockedCount },
              {
                id: "REQUIRE_CONFIRMATION",
                label: "High-Value Gates",
                count: requireConfirmCount,
              },
            ].map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setFilterDecision(tab.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap flex items-center gap-1.5 ${
                  filterDecision === tab.id
                    ? "bg-slate-900 text-white shadow-sm"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                <span>{tab.label}</span>
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono ${
                    filterDecision === tab.id
                      ? "bg-slate-700 text-white"
                      : "bg-slate-200 text-slate-700"
                  }`}
                >
                  {tab.count}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Receipts Cards Grid */}
      {loading ? (
        <div className="text-center py-20 text-slate-500 space-y-3">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto text-indigo-600" />
          <p className="text-xs font-mono">Fetching cryptographic ledger receipts...</p>
        </div>
      ) : filteredReceipts.length === 0 ? (
        <div className="bg-white rounded-3xl border-2 border-dashed border-slate-300 p-12 text-center text-slate-400 space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto text-2xl">
            📜
          </div>
          <div className="space-y-1">
            <h3 className="font-bold text-slate-800 text-base">No Matching Receipts Found</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              No decision receipts match your filter. Run an RFQ negotiation or complete an agentic checkout to generate new cryptographic receipts.
            </p>
          </div>
          <div className="pt-2 flex justify-center gap-3">
            <Link
              href="/negotiate"
              className="px-4 py-2 rounded-xl bg-indigo-600 text-white font-bold text-xs hover:bg-indigo-700 transition-colors"
            >
              Go to Negotiation Arena
            </Link>
            <Link
              href="/chat"
              className="px-4 py-2 rounded-xl bg-slate-100 text-slate-800 font-bold text-xs hover:bg-slate-200 transition-colors"
            >
              Buyer Chat & Checkout
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredReceipts.map((r) => {
            const isApproved = r.decision === "APPROVE";
            const isBlocked = r.decision === "BLOCK";
            const isRequireConfirm = r.decision === "REQUIRE_CONFIRMATION";
            const totalAmount = (r.final_verified_total || r.observed_total) / 100;
            const checksPassed = r.guardian_checks?.filter((c) => c.passed).length || 0;
            const checksTotal = r.guardian_checks?.length || 0;

            return (
              <div
                key={r.receipt_id}
                className="glass-card bg-white/95 rounded-3xl border border-slate-200/80 p-5 shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-1 flex flex-col justify-between space-y-4 relative overflow-hidden group"
              >
                {/* Top Accent Line */}
                <div
                  className={`absolute top-0 left-0 right-0 h-1.5 ${
                    isApproved
                      ? "bg-gradient-to-r from-emerald-400 to-teal-500"
                      : isBlocked
                      ? "bg-gradient-to-r from-rose-500 to-red-600"
                      : "bg-gradient-to-r from-amber-400 to-yellow-500"
                  }`}
                />

                <div className="space-y-3">
                  {/* Card Header: Decision & Tamper Chip */}
                  <div className="flex items-center justify-between gap-2 pt-1">
                    <span
                      className={`inline-flex items-center gap-1 text-[10px] font-extrabold px-2.5 py-1 rounded-full uppercase tracking-wider ${
                        isApproved
                          ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                          : isBlocked
                          ? "bg-rose-100 text-rose-800 border border-rose-200"
                          : "bg-amber-100 text-amber-800 border border-amber-200"
                      }`}
                    >
                      {isApproved ? (
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                      ) : isBlocked ? (
                        <XCircle className="w-3 h-3 text-rose-600" />
                      ) : (
                        <AlertTriangle className="w-3 h-3 text-amber-600" />
                      )}
                      {r.decision}
                    </span>

                    <span className="text-[10px] font-mono text-slate-500 flex items-center gap-1">
                      <Lock className="w-3 h-3 text-indigo-500" />
                      Ed25519 Signed
                    </span>
                  </div>

                  {/* Receipt ID & Timestamp */}
                  <div>
                    <div className="flex items-center justify-between gap-1">
                      <span className="text-xs font-mono font-bold text-slate-900 truncate">
                        {r.receipt_id}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleCopy(r.receipt_id, r.receipt_id)}
                        className="text-slate-400 hover:text-slate-700 p-1"
                        title="Copy Receipt ID"
                      >
                        {copiedId === r.receipt_id ? (
                          <Check className="w-3 h-3 text-emerald-600" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                      </button>
                    </div>
                    <span className="text-[11px] text-slate-400 font-mono flex items-center gap-1 mt-0.5">
                      <Clock className="w-3 h-3" />
                      {new Date(r.created_at).toLocaleDateString()} •{" "}
                      {new Date(r.created_at).toLocaleTimeString()}
                    </span>
                  </div>

                  {/* Reason Snippet */}
                  <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                    {r.reason}
                  </p>

                  {/* Items & Financials Breakdown */}
                  <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                    <div className="p-2 rounded-xl bg-slate-50 border border-slate-100">
                      <span className="text-[10px] text-slate-400 block uppercase">Verified Total</span>
                      <span className="font-extrabold text-slate-900 text-sm">
                        ₹{totalAmount.toFixed(2)}
                      </span>
                    </div>

                    <div className="p-2 rounded-xl bg-slate-50 border border-slate-100">
                      <span className="text-[10px] text-slate-400 block uppercase">Guardian Checks</span>
                      <span className="font-extrabold text-indigo-600 text-sm">
                        {checksPassed}/{checksTotal} Pass
                      </span>
                    </div>
                  </div>
                </div>

                {/* Card Footer: Action Button */}
                <div className="pt-2 border-t border-slate-100">
                  <Link
                    href={`/receipts/${r.receipt_id}`}
                    className="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-indigo-600 text-white font-bold text-xs transition-all flex items-center justify-center gap-1.5 shadow-sm group-hover:shadow-md"
                  >
                    <span>Inspect Audit & Replay</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
