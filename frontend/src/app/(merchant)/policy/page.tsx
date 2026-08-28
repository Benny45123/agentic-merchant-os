"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchApi } from "@/lib/api";
import {
  Shield,
  ShieldCheck,
  ShieldAlert,
  Sliders,
  Percent,
  Coins,
  Package,
  History,
  Lock,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
  Scale,
  Zap,
  ArrowRight,
  SlidersHorizontal,
  Info,
} from "lucide-react";

export default function PolicyEditorPage() {
  const [merchantId] = useState("m_001");
  const [policy, setPolicy] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [lastSavedVersion, setLastSavedVersion] = useState<number | null>(null);

  useEffect(() => {
    fetchApi<any>(`/policy?merchant_id=${merchantId}`)
      .then((data) => {
        setPolicy(data);
        setLastSavedVersion(data?.version || 1);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [merchantId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (saving) return;
    setSaving(true);
    setSaveSuccess(false);

    try {
      const updated = await fetchApi<any>(`/policy?merchant_id=${merchantId}`, {
        method: "PUT",
        body: JSON.stringify({
          maximum_discount_pct: Number(policy.maximum_discount_pct),
          minimum_margin_pct: Number(policy.minimum_margin_pct),
          maximum_order_value: Number(policy.maximum_order_value),
          allowed_products_for_discount: policy.allowed_products_for_discount || [],
          minimum_stock_to_sell: Number(policy.minimum_stock_to_sell),
        }),
      });
      setPolicy(updated);
      setLastSavedVersion(updated?.version || (policy.version + 1));
      setSaveSuccess(true);
    } catch (err: any) {
      alert(`Policy update failed: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const applyPreset = (preset: {
    discount: number;
    margin: number;
    maxOrder: number;
    minStock: number;
  }) => {
    if (!policy) return;
    setPolicy({
      ...policy,
      maximum_discount_pct: preset.discount,
      minimum_margin_pct: preset.margin,
      maximum_order_value: preset.maxOrder,
      minimum_stock_to_sell: preset.minStock,
    });
    setSaveSuccess(false);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-28 space-y-4">
        <RefreshCw className="w-8 h-8 text-indigo-600 animate-spin" />
        <div className="text-sm font-semibold text-slate-600">Loading deterministic policy state...</div>
      </div>
    );
  }

  // Safety Score & Risk Calculations
  const maxDiscount = Number(policy?.maximum_discount_pct || 0);
  const minMargin = Number(policy?.minimum_margin_pct || 0);
  const maxOrderValuePaise = Number(policy?.maximum_order_value || 0);
  const minStock = Number(policy?.minimum_stock_to_sell || 0);

  // Buffer score: 100 - Discount - Margin (ideal range: > 45%)
  const marginStress = maxDiscount + minMargin;
  const isHighDiscountRisk = maxDiscount > 40;
  const isLowMarginRisk = minMargin < 12;
  const isTightTolerance = marginStress > 65;

  let safetyLevel = "Optimal Safety";
  let safetyColor = "text-emerald-600";
  let safetyBarWidth = "85%";
  let safetyBarColor = "bg-emerald-500";

  if (isHighDiscountRisk || isLowMarginRisk || isTightTolerance) {
    if (maxDiscount > 50 || minMargin < 8 || marginStress > 80) {
      safetyLevel = "High Risk / Aggressive";
      safetyColor = "text-rose-600";
      safetyBarWidth = "30%";
      safetyBarColor = "bg-rose-500";
    } else {
      safetyLevel = "Moderate / Narrow Buffer";
      safetyColor = "text-amber-600";
      safetyBarWidth = "60%";
      safetyBarColor = "bg-amber-500";
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in pb-12">
      {/* Top Header with Animated Guardrail Policy Visualizer */}
      <div className="bg-gradient-to-r from-white via-indigo-50/40 to-white p-6 sm:p-8 rounded-3xl border border-indigo-200/90 shadow-md relative overflow-hidden space-y-6">
        {/* Soft Ambient Light Glows */}
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-indigo-100/50 rounded-full blur-3xl pointer-events-none -z-0" />
        <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-emerald-100/40 rounded-full blur-3xl pointer-events-none -z-0" />

        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 relative z-10">
          <div className="space-y-2.5 max-w-2xl">
            {/* Animated Highlighting Badges */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-indigo-600 text-white text-xs font-black uppercase tracking-wider shadow-sm shadow-indigo-500/25 animate-pulse">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Rule 6 Guardrail Engine</span>
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-200" />
                <span className="font-mono text-[11px] text-indigo-100">Policy v{policy?.version || 1}</span>
              </span>

              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-100 text-emerald-900 border border-emerald-300 text-xs font-mono font-black shadow-2xs">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
                </span>
                <span>Zero-LLM Hard Enforcement</span>
              </span>

              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 border border-slate-200 text-[11px] font-mono font-bold">
                <Lock className="w-3 h-3 text-indigo-600" />
                <span>Immutable Version History</span>
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black text-slate-900 tracking-tight leading-tight">
              Deterministic Commercial{" "}
              <span className="bg-gradient-to-r from-indigo-600 via-indigo-700 to-violet-700 bg-clip-text text-transparent">
                Policy Guardrails
              </span>
            </h1>

            <p className="text-xs sm:text-sm text-slate-600 font-normal leading-relaxed">
              Define immutable commercial bounds. The Commerce Guardian enforces these rules deterministically on every transaction, campaign proposal, and A2A negotiation.
            </p>
          </div>

          {/* Right Action CTAs */}
          <div className="flex flex-wrap sm:flex-nowrap items-center gap-3 shrink-0">
            <Link
              href="/negotiate"
              className="px-4 py-3 rounded-2xl border border-slate-200 text-xs font-bold text-slate-700 bg-white hover:bg-slate-50 hover:border-slate-300 transition-all shadow-sm flex items-center gap-2 group"
            >
              <Scale className="w-4 h-4 text-indigo-600 group-hover:scale-110 transition-transform" />
              <span>A2A Margin Arena</span>
            </Link>

            <Link
              href="/receipts"
              className="px-4 py-3 rounded-2xl bg-indigo-50 hover:bg-indigo-100/80 border border-indigo-300 text-xs font-bold text-indigo-800 transition-all shadow-sm flex items-center gap-2 group"
            >
              <Shield className="w-4 h-4 text-indigo-600 group-hover:scale-110 transition-transform" />
              <span>Audit Receipts</span>
            </Link>
          </div>
        </div>

        {/* Animated Interactive Policy Flow Ribbon */}
        <div className="relative z-10 pt-4 border-t border-indigo-100 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs bg-white/80 p-3.5 rounded-2xl border border-indigo-100/80 shadow-2xs">
          {/* Policy Limits Node */}
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-indigo-100 text-indigo-700 border border-indigo-200 flex items-center justify-center font-bold text-base shadow-2xs">
              ⚖️
            </div>
            <div>
              <div className="font-extrabold text-slate-900 text-xs">Merchant Commercial Limits</div>
              <span className="text-[10px] text-slate-500 font-mono">15% Margin Floor, 25% Max Discount</span>
            </div>
          </div>

          {/* Animated Connecting Packets */}
          <div className="flex-1 max-w-xs flex items-center justify-center gap-2 px-3 py-1 bg-indigo-50/70 rounded-xl border border-indigo-100">
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping" />
            <span className="font-mono font-black text-[10px] text-indigo-800 uppercase tracking-widest">
              Sub-50ms Kernel Evaluation
            </span>
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping [animation-delay:0.3s]" />
          </div>

          {/* Guardian Authorization Node */}
          <div className="flex items-center gap-2.5">
            <div className="text-right">
              <div className="font-extrabold text-slate-900 text-xs">Deterministic Authorization</div>
              <span className="text-[10px] text-emerald-700 font-mono font-bold">100% Zero-Bypass Path</span>
            </div>
            <div className="w-8 h-8 rounded-xl bg-emerald-100 text-emerald-800 border border-emerald-200 flex items-center justify-center font-bold text-base shadow-2xs">
              🛡️
            </div>
          </div>
        </div>
      </div>

      {/* Safety Margin Visual Gauge Card */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
              <Scale className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900">Safety Margin & Health Meter</h3>
              <p className="text-xs text-slate-500">Live simulation of financial guardrail headroom</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-600">Guardrail Status:</span>
            <span className={`text-xs font-extrabold px-3 py-1 rounded-full bg-slate-100 border border-slate-200 ${safetyColor}`}>
              {safetyLevel}
            </span>
          </div>
        </div>

        {/* Progress bar gauge */}
        <div className="space-y-1.5">
          <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden p-0.5 border border-slate-200/80">
            <div
              className={`h-full rounded-full transition-all duration-500 ${safetyBarColor}`}
              style={{ width: safetyBarWidth }}
            />
          </div>
          <div className="flex justify-between text-[10px] font-mono text-slate-400">
            <span>High Risk (0%)</span>
            <span>Moderate (50%)</span>
            <span>Optimal Headroom (100%)</span>
          </div>
        </div>

        {/* Preset Strategies */}
        <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mr-1">
            Presets:
          </span>
          <button
            type="button"
            onClick={() =>
              applyPreset({
                discount: 15,
                margin: 25,
                maxOrder: 5000000,
                minStock: 5,
              })
            }
            className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-indigo-50 hover:text-indigo-600 border border-slate-200 transition-colors"
          >
            🛡️ Conservative (15% Disc / 25% Margin)
          </button>
          <button
            type="button"
            onClick={() =>
              applyPreset({
                discount: 25,
                margin: 18,
                maxOrder: 10000000,
                minStock: 2,
              })
            }
            className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-indigo-50 hover:text-indigo-600 border border-slate-200 transition-colors"
          >
            ⚖️ Balanced Growth (25% Disc / 18% Margin)
          </button>
          <button
            type="button"
            onClick={() =>
              applyPreset({
                discount: 35,
                margin: 12,
                maxOrder: 15000000,
                minStock: 1,
              })
            }
            className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-indigo-50 hover:text-indigo-600 border border-slate-200 transition-colors"
          >
            ⚡ Aggressive Clearance (35% Disc / 12% Margin)
          </button>
        </div>
      </div>

      {/* Save Success Banner */}
      {saveSuccess && (
        <div className="animate-celebrate p-5 rounded-2xl bg-gradient-to-r from-emerald-500/10 via-emerald-500/20 to-teal-500/10 border-2 border-emerald-500/40 text-emerald-900 shadow-lg flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold text-lg shadow-sm">
              ✓
            </div>
            <div>
              <h4 className="text-sm font-black text-emerald-950">
                Policy Version {lastSavedVersion} Published & Live!
              </h4>
              <p className="text-xs text-emerald-800">
                Deterministic Guardian will enforce these rules instantly across all checkout intents and campaigns.
              </p>
            </div>
          </div>
          <span className="text-xs font-mono font-bold bg-emerald-600 text-white px-3 py-1 rounded-lg">
            v{lastSavedVersion}
          </span>
        </div>
      )}

      {/* Main Interactive Form */}
      <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Control 1: Maximum Allowed Discount */}
            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                  <Percent className="w-4 h-4 text-indigo-600" />
                  Maximum Allowed Discount
                </label>
                <span
                  className={`text-xs font-black px-2.5 py-0.5 rounded-lg border ${
                    maxDiscount > 40
                      ? "bg-rose-100 text-rose-800 border-rose-200"
                      : maxDiscount > 25
                      ? "bg-amber-100 text-amber-800 border-amber-200"
                      : "bg-indigo-100 text-indigo-800 border-indigo-200"
                  }`}
                >
                  {maxDiscount}% Cap
                </span>
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={maxDiscount}
                  onChange={(e) => {
                    setPolicy({ ...policy, maximum_discount_pct: e.target.value });
                    setSaveSuccess(false);
                  }}
                  className="flex-1"
                />
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={policy?.maximum_discount_pct || 0}
                  onChange={(e) => {
                    setPolicy({ ...policy, maximum_discount_pct: e.target.value });
                    setSaveSuccess(false);
                  }}
                  className="w-16 px-2.5 py-1.5 text-center text-sm font-bold rounded-xl border border-slate-300 bg-white focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <span className="text-[11px] text-slate-500 block leading-tight">
                Guardian deterministically BLOCKS any promotion, upsell discount, or negotiation above this percentage.
              </span>
            </div>

            {/* Control 2: Minimum Required Margin */}
            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                  <Scale className="w-4 h-4 text-emerald-600" />
                  Minimum Required Margin
                </label>
                <span
                  className={`text-xs font-black px-2.5 py-0.5 rounded-lg border ${
                    minMargin < 10
                      ? "bg-rose-100 text-rose-800 border-rose-200"
                      : minMargin < 18
                      ? "bg-amber-100 text-amber-800 border-amber-200"
                      : "bg-emerald-100 text-emerald-800 border-emerald-200"
                  }`}
                >
                  {minMargin}% Floor
                </span>
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={minMargin}
                  onChange={(e) => {
                    setPolicy({ ...policy, minimum_margin_pct: e.target.value });
                    setSaveSuccess(false);
                  }}
                  className="flex-1"
                />
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={policy?.minimum_margin_pct || 0}
                  onChange={(e) => {
                    setPolicy({ ...policy, minimum_margin_pct: e.target.value });
                    setSaveSuccess(false);
                  }}
                  className="w-16 px-2.5 py-1.5 text-center text-sm font-bold rounded-xl border border-slate-300 bg-white focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <span className="text-[11px] text-slate-500 block leading-tight">
                Computed on effective price as <code className="font-mono text-[10px] bg-slate-200 px-1 py-0.5 rounded">(Price - Cost) / Price</code>.
              </span>
            </div>

            {/* Control 3: Maximum Order Value Ceiling */}
            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                  <Coins className="w-4 h-4 text-violet-600" />
                  Max Order Value Ceiling
                </label>
                <span className="text-xs font-black font-mono px-2.5 py-0.5 rounded-lg bg-violet-100 text-violet-900 border border-violet-200">
                  ₹{(maxOrderValuePaise / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                </span>
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min="100000"
                  max="50000000"
                  step="100000"
                  value={maxOrderValuePaise}
                  onChange={(e) => {
                    setPolicy({ ...policy, maximum_order_value: e.target.value });
                    setSaveSuccess(false);
                  }}
                  className="flex-1"
                />
                <input
                  type="number"
                  value={policy?.maximum_order_value || 0}
                  onChange={(e) => {
                    setPolicy({ ...policy, maximum_order_value: e.target.value });
                    setSaveSuccess(false);
                  }}
                  className="w-28 px-2.5 py-1.5 text-center text-xs font-mono font-bold rounded-xl border border-slate-300 bg-white focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <span className="text-[11px] text-slate-500 block leading-tight">
                Raw value in paise. Transactions exceeding ₹50,000 trigger Human-in-the-Loop approval.
              </span>
            </div>

            {/* Control 4: Minimum Stock Reserve */}
            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                  <Package className="w-4 h-4 text-amber-600" />
                  Minimum Stock Reserve
                </label>
                <span className="text-xs font-black font-mono px-2.5 py-0.5 rounded-lg bg-amber-100 text-amber-900 border border-amber-200">
                  {minStock} Units Buffer
                </span>
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min="0"
                  max="50"
                  value={minStock}
                  onChange={(e) => {
                    setPolicy({ ...policy, minimum_stock_to_sell: e.target.value });
                    setSaveSuccess(false);
                  }}
                  className="flex-1"
                />
                <input
                  type="number"
                  min="0"
                  value={policy?.minimum_stock_to_sell || 0}
                  onChange={(e) => {
                    setPolicy({ ...policy, minimum_stock_to_sell: e.target.value });
                    setSaveSuccess(false);
                  }}
                  className="w-16 px-2.5 py-1.5 text-center text-sm font-bold rounded-xl border border-slate-300 bg-white focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <span className="text-[11px] text-slate-500 block leading-tight">
                Prevents warehouse inventory from dropping below safety stock on autonomous checkout.
              </span>
            </div>
          </div>

          {/* Warning Banner if Aggressive Settings */}
          {(isHighDiscountRisk || isLowMarginRisk) && (
            <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold block">Guardrail Tolerance Advisory:</span>
                <span className="leading-snug block mt-0.5 text-amber-800">
                  {isHighDiscountRisk && "Maximum discount is set above 40%, which may erode gross profit margins. "}
                  {isLowMarginRisk && "Minimum required margin is under 12%, reducing protection against supplier cost fluctuations."}
                </span>
              </div>
            </div>
          )}

          {/* Submit CTA */}
          <div className="pt-4 border-t border-slate-100">
            <button
              type="submit"
              disabled={saving}
              className="w-full py-4 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 hover:from-slate-800 hover:to-indigo-900 disabled:opacity-50 text-white font-extrabold text-sm shadow-xl shadow-slate-900/20 transition-all flex items-center justify-center gap-2 group"
            >
              {saving ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Committing Versioned Policy (Rule 6)...</span>
                </>
              ) : (
                <>
                  <Lock className="w-4 h-4 text-indigo-400 group-hover:scale-110 transition-transform" />
                  <span>Save Policy (Generates Version {policy?.version ? policy.version + 1 : 2})</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Audit & Immutability Guarantee Footer Card */}
      <div className="p-5 rounded-2xl bg-slate-100 border border-slate-200/80 text-xs text-slate-600 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <History className="w-4 h-4 text-slate-500" />
          <span>
            <strong>Deterministic Audit Contract:</strong> Policy updates generate new immutable records. Prior receipts retain their historical snapshot for zero-dispute audit replay.
          </span>
        </div>
        <span className="text-[10px] font-mono px-2 py-1 rounded bg-white border border-slate-200 font-bold">
          SHA-256 Verified
        </span>
      </div>
    </div>
  );
}

