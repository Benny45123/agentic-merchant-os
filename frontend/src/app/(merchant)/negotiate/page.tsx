"use client";

import { useState } from "react";
import Link from "next/link";
import {
  submitRFQ,
  acceptNegotiatedOffer,
  RFQResponseData,
  CounterOfferOption,
  NegotiationSettlementData,
} from "@/lib/api";
import {
  Shield,
  Zap,
  TrendingUp,
  ShoppingCart,
  BarChart3,
  Target,
  Lock,
  ArrowRight,
  ArrowLeftRight,
  Sparkles,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ChevronRight,
  Play,
  RefreshCw,
  Bot,
  Store,
  Copy,
  Check,
  Scale,
  DollarSign,
  Percent,
  Cpu,
  Activity,
  Layers,
  ArrowUpRight,
  Sliders,
  ExternalLink,
} from "lucide-react";

export default function NegotiationArenaPage() {
  const [sku, setSku] = useState("HP-001");
  const [qty, setQty] = useState(3);
  const [targetPriceInr, setTargetPriceInr] = useState(4100);
  const [loading, setLoading] = useState(false);
  const [settlingOptionId, setSettlingOptionId] = useState<string | null>(null);

  const [rfqResponse, setRfqResponse] = useState<RFQResponseData | null>(null);
  const [settlementData, setSettlementData] = useState<NegotiationSettlementData | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [copiedText, setCopiedText] = useState<string | null>(null);

  const catalogProducts: Record<
    string,
    { name: string; catalogPrice: number; cost: number; tag: string; icon: string }
  > = {
    "HP-001": {
      name: "AeroSound Wireless Headphones",
      catalogPrice: 4499,
      cost: 3000,
      tag: "Flagship Audio",
      icon: "🎧",
    },
    "HP-002": {
      name: "AeroSound Sport Earbuds",
      catalogPrice: 2999,
      cost: 1800,
      tag: "Activewear",
      icon: "⚡",
    },
    "SPK-001": {
      name: "AeroSound SoundBar Pro",
      catalogPrice: 8999,
      cost: 6000,
      tag: "Home Theater",
      icon: "🔊",
    },
  };

  const currentProd = catalogProducts[sku] || catalogProducts["HP-001"];
  const catalogTotal = currentProd.catalogPrice * qty;
  const buyerTargetTotal = targetPriceInr * qty;
  const totalCost = currentProd.cost * qty;
  const merchantGrossProfit = buyerTargetTotal - totalCost;
  const buyerProposedMargin =
    buyerTargetTotal > 0 ? ((buyerTargetTotal - totalCost) / buyerTargetTotal) * 100 : 0;
  const buyerSavings = catalogTotal - buyerTargetTotal;
  const buyerSavingsPct = catalogTotal > 0 ? (buyerSavings / catalogTotal) * 100 : 0;

  // Margin classification:
  // Red: < 15% floor
  // Yellow: 15% - 25% boundary zone
  // Green: > 25% optimal zone
  const isFloorBreached = buyerProposedMargin < 15.0;
  const isBoundaryZone = buyerProposedMargin >= 15.0 && buyerProposedMargin <= 25.0;
  const isOptimalZone = buyerProposedMargin > 25.0;

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(id);
    setTimeout(() => setCopiedText(null), 2000);
  };

  const handleRunRFQ = async () => {
    setLoading(true);
    setErrorMsg(null);
    setSettlementData(null);
    try {
      const res = await submitRFQ({
        sku,
        qty,
        target_unit_price_paise: targetPriceInr * 100,
      });
      setRfqResponse(res);
    } catch (err: any) {
      setErrorMsg(err.message || "RFQ submission failed");
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptOffer = async (optionId: string) => {
    if (!rfqResponse) return;
    setSettlingOptionId(optionId);
    setErrorMsg(null);
    try {
      const settlement = await acceptNegotiatedOffer({
        session_id: rfqResponse.session_id,
        option_id: optionId,
        buyer_id: "b_001",
        merchant_id: "m_001",
      });
      setSettlementData(settlement);
    } catch (err: any) {
      setErrorMsg(err.message || "Offer settlement failed");
    } finally {
      setSettlingOptionId(null);
    }
  };

  const applyPreset = (presetSku: string, presetQty: number, presetPrice: number) => {
    setSku(presetSku);
    setQty(presetQty);
    setTargetPriceInr(presetPrice);
    setRfqResponse(null);
    setSettlementData(null);
    setErrorMsg(null);
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Header with Animated Dual-AI Bilateral Visualizer */}
      <div className="bg-gradient-to-r from-white via-indigo-50/40 to-white p-6 sm:p-8 rounded-3xl border border-indigo-200/90 shadow-md relative overflow-hidden space-y-6">
        {/* Soft Ambient Light Glows */}
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-indigo-100/50 rounded-full blur-3xl pointer-events-none -z-0" />
        <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-emerald-100/40 rounded-full blur-3xl pointer-events-none -z-0" />

        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 relative z-10">
          <div className="space-y-2.5 max-w-2xl">
            {/* Animated Highlighting Badges */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-indigo-600 text-white text-xs font-black uppercase tracking-wider shadow-sm shadow-indigo-500/25 animate-pulse">
                <ArrowLeftRight className="w-3.5 h-3.5" />
                <span>Dual-AI Bilateral Protocol</span>
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-200" />
                <span className="font-mono text-[11px] text-indigo-100">Reverse Auction</span>
              </span>

              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-100 text-emerald-900 border border-emerald-300 text-xs font-mono font-black shadow-2xs">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
                </span>
                <span>Sub-50ms Equilibrium Gate</span>
              </span>

              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 border border-slate-200 text-[11px] font-mono font-bold">
                <Lock className="w-3 h-3 text-indigo-600" />
                <span>Ed25519 Mandate Verified</span>
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black text-slate-900 tracking-tight leading-tight">
              Autonomous A2A Dynamic{" "}
              <span className="bg-gradient-to-r from-indigo-600 via-indigo-700 to-violet-700 bg-clip-text text-transparent">
                Negotiation Arena
              </span>
            </h1>

            <p className="text-xs sm:text-sm text-slate-600 font-normal leading-relaxed">
              External Buyer AI agents submit target RFQ procurement quotes. The Merchant Pricing Agent evaluates catalog elasticity curves and dynamically formulates margin-maximizing counter-offers with zero human intervention.
            </p>
          </div>

          {/* Right Action CTAs */}
          <div className="flex flex-wrap sm:flex-nowrap items-center gap-3 shrink-0">
            <Link
              href="/dashboard"
              className="px-4 py-3 rounded-2xl border border-slate-200 text-xs font-bold text-slate-700 bg-white hover:bg-slate-50 hover:border-slate-300 transition-all shadow-sm flex items-center gap-2 group"
            >
              <BarChart3 className="w-4 h-4 text-indigo-600 group-hover:scale-110 transition-transform" />
              <span>Live Telemetry</span>
            </Link>

            <Link
              href="/policy"
              className="px-4 py-3 rounded-2xl bg-indigo-50 hover:bg-indigo-100/80 border border-indigo-300 text-xs font-bold text-indigo-800 transition-all shadow-sm flex items-center gap-2 group"
            >
              <Shield className="w-4 h-4 text-indigo-600 group-hover:scale-110 transition-transform" />
              <span>Policy Guardrails (15% Floor)</span>
            </Link>
          </div>
        </div>

        {/* Animated Interactive Bilateral Handshake Flow Ribbon */}
        <div className="relative z-10 pt-4 border-t border-indigo-100 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs bg-white/80 p-3.5 rounded-2xl border border-indigo-100/80 shadow-2xs">
          {/* Buyer Node */}
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-indigo-100 text-indigo-700 border border-indigo-200 flex items-center justify-center font-bold text-base shadow-2xs">
              🤖
            </div>
            <div>
              <div className="font-extrabold text-slate-900 text-xs">Buyer AI Agent</div>
              <span className="text-[10px] text-slate-500 font-mono">ai_buyer_agent_procure_42</span>
            </div>
          </div>

          {/* Animated Connecting Packets */}
          <div className="flex-1 max-w-xs flex items-center justify-center gap-2 px-3 py-1 bg-indigo-50/70 rounded-xl border border-indigo-100">
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping" />
            <span className="font-mono font-black text-[10px] text-indigo-800 uppercase tracking-widest">
              Live RFQ Handshake
            </span>
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping [animation-delay:0.3s]" />
          </div>

          {/* Merchant Node */}
          <div className="flex items-center gap-2.5">
            <div className="text-right">
              <div className="font-extrabold text-slate-900 text-xs">Merchant Pricing Kernel</div>
              <span className="text-[10px] text-emerald-700 font-mono font-bold">15% Cost Floor Gate</span>
            </div>
            <div className="w-8 h-8 rounded-xl bg-emerald-100 text-emerald-800 border border-emerald-200 flex items-center justify-center font-bold text-base shadow-2xs">
              🏪
            </div>
          </div>
        </div>
      </div>

      {/* Main Interactive Grid */}
      <div className="grid lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: RFQ Builder & Dynamic Margin Simulator */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-sm space-y-6 relative overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
                  <Sliders className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-slate-900">Buyer Agent RFQ Builder</h2>
                  <p className="text-[11px] text-slate-500">Tune parameters to simulate A2A auction</p>
                </div>
              </div>
              <span className="text-[10px] font-bold px-2 py-1 rounded-md bg-slate-100 text-slate-600 uppercase font-mono">
                Interactive
              </span>
            </div>

            {/* Target Product Picker */}
            <div className="space-y-2">
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                <ShoppingCart className="w-3.5 h-3.5 text-slate-500" />
                Target Product SKU:
              </label>
              <div className="grid grid-cols-1 gap-2">
                {Object.entries(catalogProducts).map(([key, prod]) => {
                  const isSelected = sku === key;
                  return (
                    <button
                      key={key}
                      type="button"
                      onClick={() => {
                        setSku(key);
                        setTargetPriceInr(Math.round(prod.catalogPrice * 0.9));
                      }}
                      className={`p-3 rounded-2xl text-left border transition-all flex items-center justify-between ${
                        isSelected
                          ? "bg-indigo-50/90 border-indigo-400 shadow-sm ring-2 ring-indigo-500/20"
                          : "bg-slate-50/70 border-slate-200 hover:bg-slate-100/80"
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{prod.icon}</span>
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-slate-900">{prod.name}</span>
                            <span className="text-[9px] px-1.5 py-0.5 rounded font-mono bg-slate-200 text-slate-700">
                              {key}
                            </span>
                          </div>
                          <div className="flex items-center gap-3 text-[11px] text-slate-500 mt-0.5 font-mono">
                            <span>Catalog: ₹{prod.catalogPrice.toLocaleString()}</span>
                            <span>•</span>
                            <span>COGS: ₹{prod.cost.toLocaleString()}</span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="text-[10px] font-bold text-indigo-700 bg-indigo-100/80 px-2 py-0.5 rounded-full">
                          {prod.tag}
                        </span>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Quantity Selector */}
            <div className="space-y-2">
              <div className="flex justify-between items-center text-xs">
                <label className="font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-slate-500" />
                  Quantity Requested:
                </label>
                <span className="font-mono font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded text-xs">
                  {qty} {qty === 1 ? "Unit" : "Units"}
                </span>
              </div>
              <div className="flex items-center gap-2">
                {[1, 3, 5, 10].map((num) => (
                  <button
                    key={num}
                    type="button"
                    onClick={() => setQty(num)}
                    className={`flex-1 py-2 rounded-xl text-xs font-bold border transition-all ${
                      qty === num
                        ? "bg-indigo-600 text-white border-indigo-600 shadow-sm scale-[1.02]"
                        : "bg-white text-slate-700 border-slate-200 hover:bg-slate-50"
                    }`}
                  >
                    {num}x
                  </button>
                ))}
                <div className="flex items-center bg-slate-100 rounded-xl p-1 border border-slate-200">
                  <button
                    type="button"
                    onClick={() => setQty(Math.max(1, qty - 1))}
                    className="w-7 h-7 rounded-lg bg-white text-slate-700 font-bold hover:bg-slate-200 flex items-center justify-center text-xs shadow-2xs"
                  >
                    -
                  </button>
                  <span className="w-8 text-center text-xs font-mono font-bold text-slate-800">
                    {qty}
                  </span>
                  <button
                    type="button"
                    onClick={() => setQty(Math.min(20, qty + 1))}
                    className="w-7 h-7 rounded-lg bg-white text-slate-700 font-bold hover:bg-slate-200 flex items-center justify-center text-xs shadow-2xs"
                  >
                    +
                  </button>
                </div>
              </div>
            </div>

            {/* Buyer Target Price Slider */}
            <div className="space-y-3 pt-1">
              <div className="flex justify-between items-center">
                <label className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                  <DollarSign className="w-3.5 h-3.5 text-slate-500" />
                  Buyer Target Unit Price:
                </label>
                <div className="flex items-center gap-1">
                  <span className="text-lg font-mono font-extrabold text-indigo-600">
                    ₹{targetPriceInr.toLocaleString()}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">/unit</span>
                </div>
              </div>

              <input
                type="range"
                min={Math.round(currentProd.cost * 0.75)}
                max={currentProd.catalogPrice}
                step={50}
                value={targetPriceInr}
                onChange={(e) => setTargetPriceInr(Number(e.target.value))}
                className="w-full accent-indigo-600 cursor-pointer"
              />

              <div className="flex justify-between text-[11px] font-mono text-slate-500">
                <span className="text-rose-600 font-bold">Cost Floor: ₹{currentProd.cost.toLocaleString()}</span>
                <span className="text-slate-700 font-bold">MSRP: ₹{currentProd.catalogPrice.toLocaleString()}</span>
              </div>

              {/* Quick Stepper Pills */}
              <div className="flex justify-between gap-1 pt-1">
                {[-200, -100, +100, +200].map((delta) => (
                  <button
                    key={delta}
                    type="button"
                    onClick={() => {
                      const next = Math.max(
                        Math.round(currentProd.cost * 0.75),
                        Math.min(currentProd.catalogPrice, targetPriceInr + delta)
                      );
                      setTargetPriceInr(next);
                    }}
                    className="flex-1 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-[11px] font-mono font-semibold text-slate-700 transition-colors"
                  >
                    {delta > 0 ? `+₹${delta}` : `-₹${Math.abs(delta)}`}
                  </button>
                ))}
              </div>
            </div>

            {/* Dynamic Margin Gauge (User Praised Feature!) */}
            <div
              className={`p-4 sm:p-5 rounded-2xl border transition-all duration-500 relative overflow-hidden shadow-md ${
                isFloorBreached
                  ? "bg-gradient-to-br from-rose-950 via-rose-900 to-slate-900 border-rose-500/50 text-rose-100 animate-rose-glow"
                  : isBoundaryZone
                  ? "bg-gradient-to-br from-amber-950 via-amber-900 to-slate-900 border-amber-500/50 text-amber-100 animate-amber-glow"
                  : "bg-gradient-to-br from-emerald-950 via-emerald-900 to-slate-900 border-emerald-500/50 text-emerald-100 animate-emerald-glow"
              }`}
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <span className="text-[10px] font-extrabold uppercase tracking-wider block text-slate-300">
                    Autonomous Policy Margin Gauge
                  </span>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-2xl font-black font-mono tracking-tight">
                      {buyerProposedMargin.toFixed(1)}%
                    </span>
                    <span className="text-xs text-slate-400 font-mono">Gross Margin</span>
                  </div>
                </div>

                <div className="text-right">
                  <span
                    className={`inline-flex items-center gap-1 text-[11px] font-extrabold px-2.5 py-1 rounded-full border uppercase tracking-wider ${
                      isFloorBreached
                        ? "bg-rose-500/30 text-rose-200 border-rose-400/40"
                        : isBoundaryZone
                        ? "bg-amber-500/30 text-amber-200 border-amber-400/40"
                        : "bg-emerald-500/30 text-emerald-200 border-emerald-400/40"
                    }`}
                  >
                    {isFloorBreached ? (
                      <>
                        <XCircle className="w-3.5 h-3.5 text-rose-400" />
                        Floor Breached (&lt;15%)
                      </>
                    ) : isBoundaryZone ? (
                      <>
                        <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                        Boundary (15-25%)
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                        Optimal (&gt;25%)
                      </>
                    )}
                  </span>
                </div>
              </div>

              {/* Multi-tier Gradient Gauge Bar */}
              <div className="space-y-1.5">
                <div className="relative w-full bg-slate-800/90 rounded-full h-3.5 overflow-hidden border border-slate-700/80 p-0.5 shadow-inner">
                  {/* Floor Line Marker at 15% */}
                  <div
                    className="absolute top-0 bottom-0 w-0.5 bg-rose-400 z-20 shadow-[0_0_8px_rgba(244,63,94,1)]"
                    style={{ left: "30%" }}
                    title="15% Minimum Margin Floor"
                  />
                  {/* Target Line Marker at 25% */}
                  <div
                    className="absolute top-0 bottom-0 w-0.5 bg-amber-400 z-20 shadow-[0_0_8px_rgba(245,158,11,1)]"
                    style={{ left: "50%" }}
                    title="25% Target Margin"
                  />

                  {/* Dynamic Progress Fill */}
                  <div
                    className={`h-full rounded-full transition-all duration-500 ease-out ${
                      isFloorBreached
                        ? "bg-gradient-to-r from-rose-600 via-rose-500 to-rose-400"
                        : isBoundaryZone
                        ? "bg-gradient-to-r from-rose-500 via-amber-500 to-amber-400"
                        : "bg-gradient-to-r from-amber-500 via-emerald-500 to-teal-400"
                    }`}
                    style={{
                      width: `${Math.max(4, Math.min(100, buyerProposedMargin * 2))}%`,
                    }}
                  />
                </div>

                <div className="flex justify-between text-[10px] font-mono text-slate-300 px-0.5">
                  <span className="text-rose-400 font-bold">0%</span>
                  <span className="text-rose-300 font-bold">| 15% Floor</span>
                  <span className="text-amber-300 font-bold">| 25% Target</span>
                  <span className="text-emerald-300 font-bold">50%+</span>
                </div>
              </div>

              {/* Headroom / Deficit Telemetry */}
              <div className="mt-3 pt-2.5 border-t border-white/10 flex justify-between items-center text-xs font-mono">
                <span className="text-slate-300">Policy Headroom:</span>
                <span
                  className={`font-bold ${
                    isFloorBreached ? "text-rose-400" : isBoundaryZone ? "text-amber-300" : "text-emerald-300"
                  }`}
                >
                  {isFloorBreached
                    ? `${(15.0 - buyerProposedMargin).toFixed(1)}% below required floor`
                    : `+${(buyerProposedMargin - 15.0).toFixed(1)}% headroom above floor`}
                </span>
              </div>
            </div>

            {/* Live Catalog vs Proposal Cost Breakdown Table */}
            <div className="bg-slate-50/90 rounded-2xl p-4 border border-slate-200 space-y-2.5">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                Live Financial Breakdown ({qty}x {sku})
              </span>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2.5 rounded-xl bg-white border border-slate-200">
                  <span className="text-[10px] text-slate-500 block">Catalog MSRP Total</span>
                  <span className="font-mono font-bold text-slate-800 text-sm">
                    ₹{catalogTotal.toLocaleString()}
                  </span>
                </div>
                <div className="p-2.5 rounded-xl bg-white border border-slate-200">
                  <span className="text-[10px] text-slate-500 block">Buyer Proposed RFQ</span>
                  <span className="font-mono font-bold text-indigo-600 text-sm">
                    ₹{buyerTargetTotal.toLocaleString()}
                  </span>
                </div>
                <div className="p-2.5 rounded-xl bg-white border border-slate-200">
                  <span className="text-[10px] text-slate-500 block">Base COGS Cost</span>
                  <span className="font-mono font-bold text-slate-600 text-sm">
                    ₹{totalCost.toLocaleString()}
                  </span>
                </div>
                <div className="p-2.5 rounded-xl bg-white border border-slate-200">
                  <span className="text-[10px] text-slate-500 block">Merchant Gross Profit</span>
                  <span
                    className={`font-mono font-bold text-sm ${
                      merchantGrossProfit > 0 ? "text-emerald-600" : "text-rose-600"
                    }`}
                  >
                    ₹{merchantGrossProfit.toLocaleString()}
                  </span>
                </div>
              </div>

              <div className="p-2.5 rounded-xl bg-indigo-50 border border-indigo-200 text-xs flex justify-between items-center font-mono">
                <span className="text-indigo-900 font-medium">Buyer Savings vs MSRP:</span>
                <span className="font-bold text-indigo-700">
                  ₹{buyerSavings.toLocaleString()} ({buyerSavingsPct.toFixed(1)}% OFF)
                </span>
              </div>
            </div>

            {/* Run Button */}
            <button
              type="button"
              onClick={handleRunRFQ}
              disabled={loading}
              className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-indigo-600 via-indigo-700 to-violet-700 hover:from-indigo-500 hover:to-violet-600 disabled:opacity-50 text-white font-extrabold text-sm shadow-lg shadow-indigo-600/20 transition-all transform hover:-translate-y-0.5 active:translate-y-0 flex items-center justify-center gap-2 group"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Computing Autonomous Counter-Offers...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-indigo-200 group-hover:scale-125 transition-transform" />
                  <span>Submit Autonomous RFQ to Pricing Agent</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </div>

          {/* Quick Scenario Preset Buttons (Clean White Card) */}
          <div className="bg-white text-slate-900 border border-slate-200 rounded-3xl p-5 space-y-3 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center gap-1.5">
                <Target className="w-3.5 h-3.5 text-indigo-600" />
                1-Click Demo Scenarios:
              </span>
              <span className="text-[10px] font-mono text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200 font-bold">
                Preset RFQs
              </span>
            </div>

            <div className="space-y-2">
              <button
                type="button"
                onClick={() => applyPreset("HP-001", 3, 4100)}
                className="w-full text-left p-3 rounded-2xl bg-slate-50 hover:bg-indigo-50/50 border border-slate-200 hover:border-indigo-300 text-xs text-slate-800 font-medium transition-all flex items-center justify-between group"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-emerald-700 font-bold">🎯 Scenario A: Valid RFQ</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-100 text-emerald-800 font-mono font-bold">
                      26.8% Margin
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    3x HP-001 @ ₹4,100 (Passes 15% floor, triggers direct split & bundle sweetener)
                  </p>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-600 group-hover:translate-x-0.5 transition-all" />
              </button>

              <button
                type="button"
                onClick={() => applyPreset("HP-001", 3, 3200)}
                className="w-full text-left p-3 rounded-2xl bg-slate-50 hover:bg-rose-50/50 border border-slate-200 hover:border-rose-300 text-xs text-slate-800 font-medium transition-all flex items-center justify-between group"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-rose-700 font-bold">🛑 Scenario B: Adversarial Floor Breach</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-rose-100 text-rose-800 font-mono font-bold">
                      6.25% Margin
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    3x HP-001 @ ₹3,200 (Breaches 15% floor, triggers autonomous defensive counter)
                  </p>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-rose-600 group-hover:translate-x-0.5 transition-all" />
              </button>

              <button
                type="button"
                onClick={() => applyPreset("SPK-001", 2, 8200)}
                className="w-full text-left p-3 rounded-2xl bg-slate-50 hover:bg-purple-50/50 border border-slate-200 hover:border-purple-300 text-xs text-slate-800 font-medium transition-all flex items-center justify-between group"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-purple-700 font-bold">🔊 Scenario C: SoundBar Pro B2B</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-purple-100 text-purple-800 font-mono font-bold">
                      26.8% Margin
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    2x SPK-001 @ ₹8,200 (High-ticket institutional procurement)
                  </p>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-purple-600 group-hover:translate-x-0.5 transition-all" />
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Bilateral Negotiation Transcript & Counter-Offers */}
        <div className="lg:col-span-7 space-y-6">
          {errorMsg && (
            <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-start gap-3 shadow-sm animate-slide-up">
              <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold block">Negotiation Protocol Error</span>
                <span>{errorMsg}</span>
              </div>
            </div>
          )}

          {/* Empty State */}
          {!rfqResponse && !loading && (
            <div className="bg-white rounded-3xl border-2 border-dashed border-slate-300 p-12 text-center text-slate-400 space-y-4 shadow-sm">
              <div className="w-16 h-16 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto text-3xl shadow-inner animate-float">
                🤝
              </div>
              <div className="space-y-1">
                <h3 className="font-bold text-slate-800 text-lg">Negotiation Arena Ready</h3>
                <p className="text-xs text-slate-500 max-w-md mx-auto leading-relaxed">
                  Configure your product parameters on the left and click{" "}
                  <strong className="text-indigo-600">"Submit Autonomous RFQ"</strong> or choose a 1-click scenario to see the External Buyer Agent and Merchant Pricing Agent negotiate real-time counter-offers.
                </p>
              </div>

              <div className="pt-4 flex flex-wrap items-center justify-center gap-4 text-[11px] text-slate-500">
                <span className="flex items-center gap-1">
                  <Check className="w-3.5 h-3.5 text-emerald-500" />
                  Zero-LLM Margin Floor Gating
                </span>
                <span className="flex items-center gap-1">
                  <Check className="w-3.5 h-3.5 text-emerald-500" />
                  Bundle Sweetener Optimizer
                </span>
                <span className="flex items-center gap-1">
                  <Check className="w-3.5 h-3.5 text-emerald-500" />
                  Deterministic Audit Trail
                </span>
              </div>
            </div>
          )}

          {/* Clean White Science Loading Radar Animation */}
          {loading && (
            <div className="bg-white rounded-3xl p-10 border border-slate-200 text-slate-900 shadow-md space-y-6 text-center animate-pulse">
              <div className="relative w-20 h-20 mx-auto">
                <div className="absolute inset-0 rounded-full border-2 border-indigo-300 animate-ping" />
                <div className="w-20 h-20 rounded-full bg-indigo-50 border-2 border-indigo-500 flex items-center justify-center text-3xl shadow-md">
                  ⚡
                </div>
              </div>
              <div className="space-y-2">
                <h3 className="text-base font-bold text-slate-900">Transmitting A2A RFQ Payload...</h3>
                <p className="text-xs text-slate-500 font-mono max-w-sm mx-auto">
                  Evaluating pricing elasticity curves, COGS margin constraints, and bundle inventory attachments in sub-50ms...
                </p>
              </div>

              <div className="flex justify-center items-center gap-2 pt-2">
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-600 typing-dot-1" />
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-600 typing-dot-2" />
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-600 typing-dot-3" />
              </div>
            </div>
          )}

          {/* Active RFQ Response */}
          {rfqResponse && (
            <div className="space-y-6 animate-slide-up">
              {/* Bilateral A2A Dialogue Feed (Clean White Science Card) */}
              <div className="bg-white rounded-3xl p-6 text-slate-900 space-y-5 shadow-sm border border-slate-200">
                <div className="flex flex-wrap items-center justify-between border-b border-slate-100 pb-4 gap-2">
                  <div className="flex items-center gap-2.5">
                    <span className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse shadow-sm" />
                    <span className="font-extrabold text-xs uppercase tracking-wider text-slate-800">
                      Bilateral A2A Protocol Transcript
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-mono text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-lg border border-indigo-200 font-bold">
                      Session: {rfqResponse.session_id.substring(0, 16)}...
                    </span>
                    <span className="text-[11px] font-mono font-bold text-slate-600 bg-slate-100 px-2 py-1 rounded-lg border border-slate-200">
                      Round {rfqResponse.round_index}/3
                    </span>
                  </div>
                </div>

                {/* Buyer Agent Message Card */}
                <div className="flex items-start gap-3.5 p-4 rounded-2xl bg-indigo-50/50 border border-indigo-100 shadow-2xs">
                  <div className="w-10 h-10 rounded-2xl bg-indigo-100 text-indigo-700 border border-indigo-200 flex items-center justify-center text-xl shrink-0 shadow-2xs">
                    🤖
                  </div>
                  <div className="space-y-1.5 flex-1 min-w-0">
                    <div className="flex flex-wrap items-center justify-between gap-1">
                      <span className="font-bold text-indigo-900 text-xs flex items-center gap-1.5">
                        External Buyer Agent
                        <span className="text-[10px] font-mono text-slate-500 font-normal">
                          (ai_buyer_agent_procure_42)
                        </span>
                      </span>
                      <span className="text-[10px] font-mono text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded border border-emerald-200 flex items-center gap-1 font-bold">
                        <Lock className="w-2.5 h-2.5" />
                        Signed Mandate
                      </span>
                    </div>

                    <div className="text-xs text-slate-800 leading-relaxed bg-white p-3 rounded-xl border border-indigo-100 shadow-2xs">
                      "I propose to purchase{" "}
                      <strong className="text-slate-900 font-semibold">
                        {qty}x {currentProd.name}
                      </strong>{" "}
                      at a target price of{" "}
                      <strong className="text-indigo-700 font-mono font-bold">
                        ₹{targetPriceInr.toLocaleString()}.00/unit
                      </strong>{" "}
                      (Total: <strong className="text-slate-900 font-mono">₹{buyerTargetTotal.toLocaleString()}.00</strong>). Can you fulfill under our spending mandate?"
                    </div>
                  </div>
                </div>

                {/* Merchant Agent Response Card */}
                <div
                  className={`flex items-start gap-3.5 p-4 rounded-2xl border shadow-2xs ${
                    rfqResponse.status === "REJECTED_MARGIN_FLOOR"
                      ? "bg-rose-50/80 border-rose-200 text-rose-900"
                      : "bg-emerald-50/80 border-emerald-200 text-emerald-900"
                  }`}
                >
                  <div
                    className={`w-10 h-10 rounded-2xl flex items-center justify-center text-xl shrink-0 border ${
                      rfqResponse.status === "REJECTED_MARGIN_FLOOR"
                        ? "bg-rose-100 border-rose-300 text-rose-700"
                        : "bg-emerald-100 border-emerald-300 text-emerald-700"
                    }`}
                  >
                    {rfqResponse.status === "REJECTED_MARGIN_FLOOR" ? "🛡️" : "🏪"}
                  </div>

                  <div className="space-y-1.5 flex-1 min-w-0">
                    <div className="flex flex-wrap items-center justify-between gap-1">
                      <span
                        className={`font-bold text-xs flex items-center gap-1.5 ${
                          rfqResponse.status === "REJECTED_MARGIN_FLOOR"
                            ? "text-rose-900"
                            : "text-emerald-900"
                        }`}
                      >
                        Merchant Pricing Agent
                        <span className="text-[10px] font-mono text-slate-500 font-normal">
                          (Autonomous Decision Engine)
                        </span>
                      </span>
                      <span
                        className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${
                          rfqResponse.status === "REJECTED_MARGIN_FLOOR"
                            ? "bg-rose-100 text-rose-800 border-rose-300"
                            : "bg-emerald-100 text-emerald-800 border-emerald-300"
                        }`}
                      >
                        {rfqResponse.status}
                      </span>
                    </div>

                    <div className="text-xs text-slate-800 leading-relaxed bg-white p-3 rounded-xl border border-slate-200 shadow-2xs">
                      <p className="font-semibold text-slate-900">{rfqResponse.reason}</p>
                      <p className="text-[11px] text-slate-600 mt-2 font-mono bg-slate-50 p-2.5 rounded-lg border border-slate-200">
                        <span className="text-indigo-700 font-bold block mb-0.5">
                          Mathematical Engine Notes:
                        </span>
                        {rfqResponse.ai_pricing_agent_notes}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Counter-Offer Formulation Cards */}
              {rfqResponse.counter_offers && rfqResponse.counter_offers.length > 0 && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-indigo-600" />
                      Bilateral Counter-Offers Formulated ({rfqResponse.counter_offers.length} Options)
                    </h3>
                    <span className="text-xs text-slate-500 font-mono">
                      Sub-50ms Equilibrium
                    </span>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    {rfqResponse.counter_offers.map((opt) => {
                      const isBundleSweetener = opt.option_type === "BUNDLE_SWEETENER";
                      const isSettling = settlingOptionId === opt.option_id;

                      return (
                        <div
                          key={opt.option_id}
                          className={`rounded-3xl border p-5 shadow-sm flex flex-col justify-between transition-all transform hover:-translate-y-1 bg-white ${
                            isBundleSweetener
                              ? "border-emerald-300 ring-2 ring-emerald-400/30 bg-gradient-to-b from-emerald-50/40 via-white to-white"
                              : "border-slate-200 hover:border-indigo-300"
                          }`}
                        >
                          <div className="space-y-3.5">
                            {/* Card Header Badges */}
                            <div className="flex justify-between items-start gap-2">
                              <span
                                className={`text-[10px] font-extrabold px-2.5 py-1 rounded-lg uppercase tracking-wider flex items-center gap-1 ${
                                  isBundleSweetener
                                    ? "bg-emerald-600 text-white shadow-2xs"
                                    : "bg-indigo-100 text-indigo-800"
                                }`}
                              >
                                {isBundleSweetener ? (
                                  <>
                                    <Sparkles className="w-3 h-3 text-emerald-100" />
                                    ★ Value Maximizer Sweetener
                                  </>
                                ) : (
                                  <>
                                    <Scale className="w-3 h-3 text-indigo-600" />
                                    Direct Price Split
                                  </>
                                )}
                              </span>

                              <span className="text-xs font-mono font-extrabold text-emerald-800 bg-emerald-100 px-2.5 py-1 rounded-lg border border-emerald-200">
                                Margin: {opt.projected_gross_margin_pct}%
                              </span>
                            </div>

                            {/* Title & Description */}
                            <div>
                              <h4 className="font-extrabold text-slate-900 text-sm leading-snug">
                                {opt.title}
                              </h4>
                              <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                                {opt.description}
                              </p>
                            </div>

                            {/* Bundled Items Breakdown */}
                            {opt.bundled_items && opt.bundled_items.length > 0 && (
                              <div className="p-3 rounded-2xl bg-emerald-50/80 border border-emerald-200 text-xs space-y-2">
                                <span className="font-bold text-emerald-950 text-[11px] flex items-center gap-1">
                                  <Sparkles className="w-3 h-3 text-emerald-600" />
                                  Included Addon Attachments:
                                </span>
                                {opt.bundled_items.map((b) => (
                                  <div
                                    key={b.addon_sku}
                                    className="flex justify-between items-center text-[11px] text-emerald-900 bg-white p-2 rounded-xl border border-emerald-100 shadow-2xs"
                                  >
                                    <div>
                                      <span className="font-bold">
                                        + {b.addon_qty}x {b.addon_name}
                                      </span>
                                      <span className="text-[10px] text-slate-500 font-mono block">
                                        SKU: {b.addon_sku}
                                      </span>
                                    </div>
                                    <div className="text-right font-mono">
                                      <span className="line-through text-slate-400 text-[10px] mr-1.5">
                                        ₹{(b.original_price_paise * b.addon_qty) / 100}
                                      </span>
                                      <span className="font-bold text-emerald-700">
                                        ₹{(b.discounted_price_paise * b.addon_qty) / 100}
                                      </span>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}

                            {/* Price & Merchant Lift Section */}
                            <div className="pt-3 border-t border-slate-100 flex flex-wrap justify-between items-end gap-2">
                              <div>
                                <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">
                                  Total Negotiated Deal
                                </span>
                                <span className="text-xl font-black text-slate-900 font-mono">
                                  ₹{(opt.total_amount_paise / 100).toLocaleString("en-IN", {
                                    minimumFractionDigits: 2,
                                  })}
                                </span>
                              </div>

                              {opt.merchant_profit_lift_paise > 0 && (
                                <div
                                  className="inline-flex items-center gap-1 text-[11px] font-extrabold text-emerald-800 bg-emerald-100 border border-emerald-300 px-2.5 py-1 rounded-xl shadow-2xs animate-badge-glow cursor-help"
                                  title="Merchant Profit Lift is the EXTRA gross profit earned above fulfilling the buyer's unbundled target price alone, achieved by bundling high-margin warranty/accessory addons."
                                >
                                  <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
                                  <span>+₹{(opt.merchant_profit_lift_paise / 100).toFixed(2)} Merchant Lift</span>
                                </div>
                              )}
                            </div>
                          </div>

                          {/* 1-Click Settlement Button */}
                          <div className="pt-4 mt-2">
                            <button
                              type="button"
                              onClick={() => handleAcceptOffer(opt.option_id)}
                              disabled={settlingOptionId !== null}
                              className={`w-full py-3 rounded-2xl font-bold text-xs shadow-md transition-all flex items-center justify-center gap-2 ${
                                isBundleSweetener
                                  ? "bg-emerald-600 hover:bg-emerald-700 text-white shadow-emerald-600/20"
                                  : "bg-slate-900 hover:bg-slate-800 text-white"
                              } disabled:opacity-50`}
                            >
                              {isSettling ? (
                                <>
                                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                                  <span>Authorizing via Guardian...</span>
                                </>
                              ) : (
                                <>
                                  <Shield className="w-3.5 h-3.5" />
                                  <span>Accept Deal & Settle via Guardian</span>
                                  <ArrowRight className="w-3.5 h-3.5" />
                                </>
                              )}
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Settlement Result Card (Clean White & Emerald Holographic Card) */}
              {settlementData && (
                <div className="relative overflow-hidden rounded-3xl bg-gradient-to-b from-emerald-50 via-white to-emerald-50/40 text-slate-900 p-6 sm:p-7 border-2 border-emerald-400 shadow-xl space-y-5 animate-celebrate">
                  {/* Header */}
                  <div className="flex flex-wrap items-center justify-between border-b border-emerald-200 pb-4 gap-3">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-2xl bg-emerald-100 border border-emerald-300 flex items-center justify-center text-2xl shadow-inner text-emerald-800">
                        🎉
                      </div>
                      <div>
                        <h4 className="font-extrabold text-emerald-950 text-base sm:text-lg">
                          Negotiated Deal Authorized & Settled!
                        </h4>
                        <p className="text-xs text-slate-600 font-medium">
                          Guardian evaluated and verified all deterministic bounds
                        </p>
                      </div>
                    </div>

                    <span className="px-3.5 py-1.5 rounded-full text-xs font-mono font-extrabold bg-emerald-100 text-emerald-800 border border-emerald-300 shadow-2xs flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                      Guardian: {settlementData.guardian_decision}
                    </span>
                  </div>

                  {/* Telemetry Metrics */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
                    <div className="bg-white p-3.5 rounded-2xl border border-emerald-200 shadow-2xs">
                      <span className="text-slate-500 block text-[10px] uppercase font-bold tracking-wider">
                        Final Settled Total
                      </span>
                      <span className="text-lg font-extrabold text-slate-900">
                        ₹{(settlementData.final_verified_total_paise / 100).toFixed(2)}
                      </span>
                    </div>

                    <div className="bg-white p-3.5 rounded-2xl border border-emerald-200 shadow-2xs">
                      <span className="text-slate-500 block text-[10px] uppercase font-bold tracking-wider">
                        Merchant Margin Achieved
                      </span>
                      <span className="text-lg font-extrabold text-emerald-700">
                        {settlementData.merchant_margin_achieved_pct}%
                      </span>
                    </div>

                    <div className="bg-white p-3.5 rounded-2xl border border-emerald-200 shadow-2xs">
                      <span className="text-slate-500 block text-[10px] uppercase font-bold tracking-wider">
                        Razorpay Order ID
                      </span>
                      <div className="flex items-center justify-between gap-1 mt-0.5">
                        <span className="text-xs font-bold text-indigo-700 truncate">
                          {settlementData.razorpay_order_id || "Pre-Authorized"}
                        </span>
                        {settlementData.razorpay_order_id && (
                          <button
                            type="button"
                            onClick={() =>
                              handleCopy(settlementData.razorpay_order_id!, "order_id")
                            }
                            className="p-1 text-slate-400 hover:text-slate-700 transition-colors"
                            title="Copy Order ID"
                          >
                            {copiedText === "order_id" ? (
                              <Check className="w-3.5 h-3.5 text-emerald-600" />
                            ) : (
                              <Copy className="w-3.5 h-3.5" />
                            )}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Replay Hash & Link */}
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pt-2">
                    <div className="flex items-center gap-2 text-xs text-slate-700 font-mono bg-white px-3 py-1.5 rounded-xl border border-emerald-200 shadow-2xs">
                      <Lock className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Replay Hash: {settlementData.replay_hash.substring(0, 16)}...</span>
                      <button
                        type="button"
                        onClick={() => handleCopy(settlementData.replay_hash, "replay_hash")}
                        className="text-slate-400 hover:text-slate-700"
                        title="Copy Replay Hash"
                      >
                        {copiedText === "replay_hash" ? (
                          <Check className="w-3 h-3 text-emerald-600" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                      </button>
                    </div>

                    <Link
                      href={`/receipts/${settlementData.receipt_id}`}
                      className="px-5 py-2.5 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs shadow-md transition-all flex items-center gap-2 group"
                    >
                      <Sparkles className="w-3.5 h-3.5 text-emerald-100 group-hover:rotate-12 transition-transform" />
                      <span>View Immutable Decision Receipt</span>
                      <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                    </Link>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
