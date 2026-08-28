"use client";

import { useState } from "react";
import Link from "next/link";
import {
  CampaignProposalData,
  activateCampaign,
  proposeCampaign,
} from "@/lib/api";
import {
  Target,
  ShieldCheck,
  ShieldAlert,
  Shield,
  Sparkles,
  Zap,
  Tag,
  CheckCircle2,
  XCircle,
  ArrowRight,
  TrendingUp,
  Coins,
  Package,
  Layers,
  Flame,
  Check,
  ShoppingBag,
  ExternalLink,
  RefreshCw,
  Sliders,
  Award,
  BarChart3,
} from "lucide-react";

export default function CampaignsPage() {
  const [merchantId] = useState("m_001");
  const [objective, setObjective] = useState("Increase sales of wireless headphones this weekend");
  const [loading, setLoading] = useState(false);
  const [proposal, setProposal] = useState<CampaignProposalData | null>(null);
  const [activated, setActivated] = useState<string | null>(null);
  const [activating, setActivating] = useState(false);

  const presetObjectives = [
    {
      id: "headphones",
      label: "Weekend Headphones Sale",
      icon: "🎧",
      text: "Increase sales of wireless headphones this weekend with targeted 15% discount",
      tag: "High Margin",
    },
    {
      id: "accessories",
      label: "Audio Accessories Bundle Attach",
      icon: "🔌",
      text: "Boost audio accessories attach rate with 10% discount on cables and cases",
      tag: "Attach Lift",
    },
    {
      id: "clearance",
      label: "Inventory Clearance",
      icon: "🏷️",
      text: "Clear excess inventory of overstocked soundbars with 20% promotional offer",
      tag: "Volume Drive",
    },
    {
      id: "flash_anc",
      label: "Flash Premium ANC Promotion",
      icon: "⚡",
      text: "Run a 48h flash deal on premium active noise cancelling audio gear",
      tag: "Conversion",
    },
  ];

  const handlePropose = async () => {
    if (!objective.trim() || loading) return;
    setLoading(true);
    setActivated(null);
    try {
      const res = await proposeCampaign(merchantId, objective);
      setProposal(res);
    } catch (err: any) {
      alert(`Proposal generation failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleActivate = async () => {
    if (!proposal || activating) return;
    setActivating(true);
    try {
      const res = await activateCampaign(proposal.proposal_id);
      setActivated(res.campaign_id);
    } catch (err: any) {
      alert(`Activation failed: ${err.message}`);
    } finally {
      setActivating(false);
    }
  };

  // Determine active step index: 0 = Propose, 1 = Guardian Validate, 2 = Catalog Activation
  const activeStep = activated ? 3 : proposal ? 2 : loading ? 1 : 0;

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fade-in pb-12">
      {/* Top Header with Animated AI Growth Engine Visualizer */}
      <div className="bg-gradient-to-r from-white via-indigo-50/40 to-white p-6 sm:p-8 rounded-3xl border border-indigo-200/90 shadow-md relative overflow-hidden space-y-6">
        {/* Soft Ambient Light Glows */}
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-indigo-100/50 rounded-full blur-3xl pointer-events-none -z-0" />
        <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-emerald-100/40 rounded-full blur-3xl pointer-events-none -z-0" />

        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 relative z-10">
          <div className="space-y-2.5 max-w-2xl">
            {/* Animated Highlighting Badges */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-indigo-600 text-white text-xs font-black uppercase tracking-wider shadow-sm shadow-indigo-500/25 animate-pulse">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Side B • AI Growth Engine</span>
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-200" />
                <span className="font-mono text-[11px] text-indigo-100">Campaign Orchestrator</span>
              </span>

              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-100 text-emerald-900 border border-emerald-300 text-xs font-mono font-black shadow-2xs">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
                </span>
                <span>Guardian Pre-Validated</span>
              </span>

              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 border border-slate-200 text-[11px] font-mono font-bold">
                <Target className="w-3 h-3 text-indigo-600" />
                <span>Bounded Promotional Scope</span>
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black text-slate-900 tracking-tight leading-tight">
              AI Campaign Strategy{" "}
              <span className="bg-gradient-to-r from-indigo-600 via-indigo-700 to-violet-700 bg-clip-text text-transparent">
                Orchestrator
              </span>
            </h1>

            <p className="text-xs sm:text-sm text-slate-600 font-normal leading-relaxed">
              State revenue goals in plain English. The AI synthesizes bounded promotional offers, deterministically validated against merchant policies before writing live discounts to the catalog.
            </p>
          </div>

          {/* Right Action CTAs */}
          <div className="flex flex-wrap sm:flex-nowrap items-center gap-3 shrink-0">
            <Link
              href="/dashboard"
              className="px-4 py-3 rounded-2xl border border-slate-200 text-xs font-bold text-slate-700 bg-white hover:bg-slate-50 hover:border-slate-300 transition-all shadow-sm flex items-center gap-2 group"
            >
              <BarChart3 className="w-4 h-4 text-indigo-600 group-hover:scale-110 transition-transform" />
              <span>Revenue Attribution</span>
            </Link>

            <Link
              href="/policy"
              className="px-4 py-3 rounded-2xl bg-indigo-50 hover:bg-indigo-100/80 border border-indigo-300 text-xs font-bold text-indigo-800 transition-all shadow-sm flex items-center gap-2 group"
            >
              <Shield className="w-4 h-4 text-indigo-600 group-hover:scale-110 transition-transform" />
              <span>Margin Policy Limits</span>
            </Link>
          </div>
        </div>

        {/* Animated Interactive Campaign Strategy Flow Ribbon */}
        <div className="relative z-10 pt-4 border-t border-indigo-100 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs bg-white/80 p-3.5 rounded-2xl border border-indigo-100/80 shadow-2xs">
          {/* Objective Node */}
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-indigo-100 text-indigo-700 border border-indigo-200 flex items-center justify-center font-bold text-base shadow-2xs">
              🎯
            </div>
            <div>
              <div className="font-extrabold text-slate-900 text-xs">Natural Language Objective</div>
              <span className="text-[10px] text-slate-500 font-mono">Headphones, Soundbars, Attach</span>
            </div>
          </div>

          {/* Animated Connecting Packets */}
          <div className="flex-1 max-w-xs flex items-center justify-center gap-2 px-3 py-1 bg-indigo-50/70 rounded-xl border border-indigo-100">
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping" />
            <span className="font-mono font-black text-[10px] text-indigo-800 uppercase tracking-widest">
              Guardian Invariant Scan
            </span>
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping [animation-delay:0.3s]" />
          </div>

          {/* Catalog Discount Node */}
          <div className="flex items-center gap-2.5">
            <div className="text-right">
              <div className="font-extrabold text-slate-900 text-xs">Active Catalog Promotion</div>
              <span className="text-[10px] text-emerald-700 font-mono font-bold">100% Margin Compliant</span>
            </div>
            <div className="w-8 h-8 rounded-xl bg-emerald-100 text-emerald-800 border border-emerald-200 flex items-center justify-center font-bold text-base shadow-2xs">
              🏷️
            </div>
          </div>
        </div>
      </div>

      {/* 3-Step Animated Progress Stepper */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
        <div className="relative flex flex-col sm:flex-row justify-between items-center gap-4">
          {/* Connector Line */}
          <div className="hidden sm:block absolute top-1/2 left-12 right-12 h-1 bg-slate-100 -translate-y-1/2 z-0">
            <div
              className="h-full bg-gradient-to-r from-indigo-600 via-violet-600 to-emerald-500 transition-all duration-700 ease-out"
              style={{
                width: activeStep === 0 ? "15%" : activeStep === 1 ? "50%" : activeStep === 2 ? "85%" : "100%",
              }}
            />
          </div>

          {/* Step 1 */}
          <div className="relative z-10 flex sm:flex-col items-center sm:text-center gap-3 w-full sm:w-auto">
            <div
              className={`w-12 h-12 rounded-2xl flex items-center justify-center font-bold text-sm transition-all duration-300 shadow-sm ${
                activeStep >= 1
                  ? "bg-indigo-600 text-white shadow-indigo-200 shadow-md ring-4 ring-indigo-50"
                  : "bg-indigo-600 text-white shadow-indigo-100 ring-4 ring-indigo-50"
              }`}
            >
              {proposal ? <Check className="w-6 h-6 stroke-[3]" /> : <Target className="w-6 h-6" />}
            </div>
            <div>
              <span className="text-xs font-bold text-slate-900 block">Step 1: Propose Intent</span>
              <span className="text-[11px] text-slate-500">Natural Language Goal</span>
            </div>
          </div>

          {/* Step 2 */}
          <div className="relative z-10 flex sm:flex-col items-center sm:text-center gap-3 w-full sm:w-auto">
            <div
              className={`w-12 h-12 rounded-2xl flex items-center justify-center font-bold text-sm transition-all duration-300 shadow-sm ${
                proposal
                  ? proposal.guardian_decision.decision === "APPROVE"
                    ? "bg-emerald-600 text-white shadow-emerald-200 ring-4 ring-emerald-50"
                    : proposal.guardian_decision.decision === "BLOCK"
                    ? "bg-rose-600 text-white shadow-rose-200 ring-4 ring-rose-50"
                    : "bg-amber-500 text-white shadow-amber-200 ring-4 ring-amber-50"
                  : loading
                  ? "bg-indigo-500 text-white animate-pulse-glow ring-4 ring-indigo-100"
                  : "bg-slate-100 text-slate-400 border border-slate-200"
              }`}
            >
              {proposal ? (
                proposal.guardian_decision.decision === "APPROVE" ? (
                  <ShieldCheck className="w-6 h-6" />
                ) : (
                  <ShieldAlert className="w-6 h-6" />
                )
              ) : loading ? (
                <RefreshCw className="w-5 h-5 animate-spin" />
              ) : (
                <Shield className="w-6 h-6" />
              )}
            </div>
            <div>
              <span className="text-xs font-bold text-slate-900 block">Step 2: Guardian Validate</span>
              <span className="text-[11px] text-slate-500">Margin & Stock Verification</span>
            </div>
          </div>

          {/* Step 3 */}
          <div className="relative z-10 flex sm:flex-col items-center sm:text-center gap-3 w-full sm:w-auto">
            <div
              className={`w-12 h-12 rounded-2xl flex items-center justify-center font-bold text-sm transition-all duration-300 shadow-sm ${
                activated
                  ? "bg-emerald-600 text-white shadow-emerald-300 shadow-lg ring-4 ring-emerald-100 animate-bounce"
                  : proposal && proposal.guardian_decision.decision !== "BLOCK"
                  ? "bg-indigo-50 text-indigo-700 border-2 border-indigo-500 animate-pulse"
                  : "bg-slate-100 text-slate-400 border border-slate-200"
              }`}
            >
              {activated ? <Award className="w-6 h-6" /> : <ShoppingBag className="w-6 h-6" />}
            </div>
            <div>
              <span className="text-xs font-bold text-slate-900 block">Step 3: Activate to Catalog</span>
              <span className="text-[11px] text-slate-500">Live Static Discount Injection</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Campaign Input & Preset Controls */}
      <div className="bg-white p-7 rounded-3xl border border-slate-200 shadow-sm space-y-6">
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
              <Zap className="w-4 h-4 text-indigo-600" />
              Merchant Revenue Objective
            </label>
            <span className="text-xs text-slate-500">Natural language input</span>
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <input
                type="text"
                value={objective}
                onChange={(e) => setObjective(e.target.value)}
                placeholder="e.g. Boost audio accessories attach rate with 10% discount..."
                className="w-full pl-4 pr-10 py-3.5 text-sm rounded-2xl border border-slate-300 bg-slate-50/50 focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent focus:outline-none transition-all shadow-inner font-medium text-slate-800"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !loading && objective.trim()) {
                    handlePropose();
                  }
                }}
              />
              {objective && (
                <button
                  type="button"
                  onClick={() => setObjective("")}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-xs px-1.5 py-0.5 rounded-full hover:bg-slate-200"
                >
                  ✕
                </button>
              )}
            </div>

            <button
              onClick={handlePropose}
              disabled={loading || !objective.trim()}
              className="px-7 py-3.5 rounded-2xl bg-gradient-to-r from-indigo-600 via-indigo-700 to-violet-700 hover:from-indigo-500 hover:to-violet-600 disabled:opacity-50 text-white font-bold text-sm shadow-md hover:shadow-indigo-500/25 transition-all flex items-center justify-center gap-2 group whitespace-nowrap"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>AI Orchestrating...</span>
                </>
              ) : (
                <>
                  <span>Propose Campaign</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </div>
        </div>

        {/* Preset Chips */}
        <div className="space-y-2.5 pt-2 border-t border-slate-100">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
            ⚡ Quick Objective Presets (Click to Load):
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
            {presetObjectives.map((preset) => (
              <button
                key={preset.id}
                type="button"
                onClick={() => setObjective(preset.text)}
                className={`p-3 rounded-xl border text-left transition-all flex flex-col justify-between gap-1.5 group ${
                  objective === preset.text
                    ? "bg-indigo-50/80 border-indigo-300 ring-2 ring-indigo-500/20 shadow-sm"
                    : "bg-slate-50/70 border-slate-200 hover:bg-indigo-50/40 hover:border-indigo-200"
                }`}
              >
                <div className="flex items-center justify-between w-full">
                  <span className="text-base">{preset.icon}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full font-semibold bg-white border border-slate-200 text-slate-600 group-hover:border-indigo-200 group-hover:text-indigo-600">
                    {preset.tag}
                  </span>
                </div>
                <div>
                  <span className="text-xs font-bold text-slate-800 block group-hover:text-indigo-600 transition-colors line-clamp-1">
                    {preset.label}
                  </span>
                  <span className="text-[11px] text-slate-500 line-clamp-2 leading-tight block mt-0.5">
                    {preset.text}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Proposal Review Card */}
      {proposal && (
        <div className="animate-slide-up bg-white rounded-3xl border border-slate-200/90 shadow-xl overflow-hidden">
          {/* Header Bar with Guardian Status Badge */}
          <div className="p-6 bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 text-white flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-indigo-400" />
                <h2 className="text-lg font-extrabold text-white tracking-tight">AI Generated Campaign Proposal</h2>
              </div>
              <span className="text-xs text-slate-400 font-mono">Proposal ID: {proposal.proposal_id}</span>
            </div>

            {/* Glowing Guardian Badge */}
            <div
              className={`px-4 py-2 rounded-2xl font-extrabold text-xs uppercase tracking-wider flex items-center gap-2 border shadow-lg ${
                proposal.guardian_decision.decision === "APPROVE"
                  ? "bg-emerald-500/20 text-emerald-300 border-emerald-400/50 shadow-emerald-500/20 animate-emerald-glow"
                  : proposal.guardian_decision.decision === "BLOCK"
                  ? "bg-rose-500/20 text-rose-300 border-rose-400/50 shadow-rose-500/20"
                  : "bg-amber-500/20 text-amber-300 border-amber-400/50 shadow-amber-500/20"
              }`}
            >
              {proposal.guardian_decision.decision === "APPROVE" ? (
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
              ) : (
                <ShieldAlert className="w-4 h-4 text-rose-400" />
              )}
              <span>Guardian: {proposal.guardian_decision.decision}</span>
            </div>
          </div>

          <div className="p-7 space-y-6">
            {/* 3 Metric Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {/* Proposed Discount */}
              <div className="p-5 rounded-2xl bg-gradient-to-br from-indigo-50/80 to-slate-50 border border-indigo-100 shadow-sm relative overflow-hidden group hover:border-indigo-300 transition-all">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center gap-1.5">
                    <Tag className="w-3.5 h-3.5 text-indigo-600" />
                    Proposed Discount
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded-md font-bold bg-indigo-600 text-white">
                    Bounded
                  </span>
                </div>
                <div className="flex items-baseline gap-1">
                  <span className="text-3xl font-black bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">
                    {proposal.discount_pct}%
                  </span>
                  <span className="text-sm font-extrabold text-indigo-600">OFF</span>
                </div>
                <span className="text-[11px] text-slate-500 block mt-1">Within merchant margin floor</span>
              </div>

              {/* Campaign Budget */}
              <div className="p-5 rounded-2xl bg-gradient-to-br from-emerald-50/60 to-slate-50 border border-emerald-100 shadow-sm relative overflow-hidden group hover:border-emerald-300 transition-all">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center gap-1.5">
                    <Coins className="w-3.5 h-3.5 text-emerald-600" />
                    Campaign Budget
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded-md font-bold bg-emerald-100 text-emerald-800">
                    Hard Cap
                  </span>
                </div>
                <div className="text-3xl font-black text-slate-900 font-mono">
                  ₹{(proposal.budget / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                </div>
                <span className="text-[11px] text-slate-500 block mt-1">Deterministic budget allotment</span>
              </div>

              {/* Eligible SKUs */}
              <div className="p-5 rounded-2xl bg-gradient-to-br from-slate-50 to-slate-100/60 border border-slate-200 shadow-sm group hover:border-slate-300 transition-all">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center gap-1.5">
                    <Package className="w-3.5 h-3.5 text-slate-700" />
                    Eligible SKUs
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded-md font-bold bg-slate-200 text-slate-800">
                    {proposal.eligible_skus.length} Items
                  </span>
                </div>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {proposal.eligible_skus.map((sku) => (
                    <span
                      key={sku}
                      className="px-2.5 py-1 rounded-lg bg-white border border-slate-300 text-xs font-mono font-bold text-slate-800 shadow-2xs"
                    >
                      {sku}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* AI Rationale Card */}
            <div className="p-4 rounded-2xl bg-gradient-to-r from-indigo-50/50 via-white to-violet-50/40 border border-indigo-100 text-xs space-y-1.5">
              <div className="flex items-center gap-1.5 text-indigo-900 font-bold">
                <Sparkles className="w-4 h-4 text-indigo-600" />
                <span>AI Strategy & Economics Rationale:</span>
              </div>
              <p className="text-slate-700 leading-relaxed pl-5 font-normal">{proposal.rationale}</p>
            </div>

            {/* Guardian Checks Breakdown */}
            <div className="rounded-2xl bg-slate-50 p-5 border border-slate-200 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  Deterministic Guardian Audit Checks
                </span>
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-200 text-slate-700">
                  {proposal.guardian_decision.checks.filter((c) => c.passed).length} / {proposal.guardian_decision.checks.length} Passed
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                {proposal.guardian_decision.checks.map((chk, i) => (
                  <div
                    key={i}
                    className={`p-3 rounded-xl border flex items-start gap-3 transition-all ${
                      chk.passed
                        ? "bg-white border-emerald-200/80 shadow-2xs"
                        : "bg-rose-50/60 border-rose-200"
                    }`}
                  >
                    <div className="mt-0.5">
                      {chk.passed ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                      ) : (
                        <XCircle className="w-4 h-4 text-rose-600 shrink-0" />
                      )}
                    </div>
                    <div className="flex-1">
                      <span className="font-mono font-bold text-slate-900 text-xs block">{chk.name}</span>
                      <span className="text-slate-500 text-[11px] block mt-0.5 leading-snug">{chk.detail}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Activate CTA Action */}
            {proposal.guardian_decision.decision !== "BLOCK" && !activated && (
              <div className="pt-2">
                <button
                  onClick={handleActivate}
                  disabled={activating}
                  className="w-full py-4 rounded-2xl bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 hover:from-emerald-500 hover:to-teal-600 disabled:opacity-60 text-white font-extrabold text-sm shadow-lg shadow-emerald-600/25 hover:shadow-emerald-600/40 transition-all flex items-center justify-center gap-2 group"
                >
                  {activating ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Writing Verified Offers to Catalog...</span>
                    </>
                  ) : (
                    <>
                      <Zap className="w-5 h-5 text-emerald-200 group-hover:scale-110 transition-transform" />
                      <span>Confirm & Activate Campaign to Catalog</span>
                      <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </>
                  )}
                </button>
              </div>
            )}

            {/* Animated Celebration Banner */}
            {activated && (
              <div className="animate-celebrate p-6 rounded-3xl bg-gradient-to-br from-emerald-900 via-slate-900 to-teal-950 text-white border-2 border-emerald-500/50 shadow-2xl shadow-emerald-500/20 space-y-4">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center text-2xl shadow-inner">
                      🎉
                    </div>
                    <div>
                      <h3 className="text-lg font-black text-emerald-300">Campaign is LIVE in Product Catalog!</h3>
                      <p className="text-xs text-slate-300">
                        Static discount offer rows have been deterministically committed. Buyers can now experience this promotion.
                      </p>
                    </div>
                  </div>
                  <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                    ID: {activated}
                  </span>
                </div>

                <div className="pt-3 border-t border-emerald-800/60 flex flex-wrap items-center gap-3">
                  <Link
                    href="/chat"
                    className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow-md hover:shadow-emerald-500/30 transition-all flex items-center gap-2"
                  >
                    <span>🛍️ Test Live in Buyer Chat</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>

                  <Link
                    href="/dashboard"
                    className="px-5 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-xs border border-white/10 transition-all flex items-center gap-2"
                  >
                    <span>📊 View Dashboard Telemetry</span>
                  </Link>

                  <button
                    onClick={() => {
                      setProposal(null);
                      setActivated(null);
                    }}
                    className="px-4 py-2.5 rounded-xl text-xs text-slate-400 hover:text-white transition-colors ml-auto"
                  >
                    + Create Another Campaign
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

