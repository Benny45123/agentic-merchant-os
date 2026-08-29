"use client";

import React, { useState, useRef } from "react";
import Link from "next/link";
import {
  ShoppingBag,
  ArrowLeftRight,
  BarChart3,
  Target,
  ShieldCheck,
  FileCheck,
  ArrowRight,
  CheckCircle2,
  Lock,
  Zap,
  Activity,
  Layers,
  Sparkles,
  TrendingUp,
  Cpu,
  Sliders,
  Compass,
  MousePointer2,
} from "lucide-react";

interface FeatureCardProps {
  feature: {
    id: string;
    step: string;
    tag: string;
    tagColor: string;
    accentGlow: string;
    spotlightColor: string;
    accentBorder: string;
    title: string;
    desc: string;
    bullets: string[];
    linkText: string;
    linkHref: string;
    icon: any;
    iconColor: string;
    previewType: string;
  };
  idx: number;
}

function InteractiveStickyCard({ feature, idx }: FeatureCardProps) {
  const outerRef = useRef<HTMLDivElement>(null);
  const cardRef = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);
  const rafId = useRef<number | null>(null);

  const Icon = feature.icon;
  const zIndexVal = 10 + idx;

  const handleMouseEnter = () => {
    setIsHovered(true);
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!outerRef.current || !cardRef.current) return;
    
    // Always measure relative to the stationary outer container to prevent feedback-loop jiggle
    const rect = outerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (rafId.current) cancelAnimationFrame(rafId.current);

    rafId.current = requestAnimationFrame(() => {
      if (!cardRef.current) return;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      // Gentle, controlled 3D tilt angles
      const rotateX = ((y - centerY) / centerY) * -3.2;
      const rotateY = ((x - centerX) / centerX) * 3.2;

      cardRef.current.style.setProperty("--mouse-x", `${x}px`);
      cardRef.current.style.setProperty("--mouse-y", `${y}px`);
      cardRef.current.style.setProperty("--rotate-x", `${rotateX}deg`);
      cardRef.current.style.setProperty("--rotate-y", `${rotateY}deg`);
      cardRef.current.style.setProperty("--spotlight-opacity", "1");
    });
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    if (rafId.current) cancelAnimationFrame(rafId.current);
    if (cardRef.current) {
      cardRef.current.style.setProperty("--rotate-x", "0deg");
      cardRef.current.style.setProperty("--rotate-y", "0deg");
      cardRef.current.style.setProperty("--spotlight-opacity", "0");
    }
  };

  return (
    <div
      id={`feature-${feature.id}`}
      style={{
        top: "100px",
        zIndex: zIndexVal,
      }}
      className="sticky mb-32 last:mb-8 transition-all duration-300"
    >
      {/* Outer Stable Event Listener Container (never transformed, eliminating oscillation) */}
      <div
        ref={outerRef}
        onMouseEnter={handleMouseEnter}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        className="relative w-full rounded-3xl"
      >
        {/* Inner Visual Container with GPU-accelerated CSS Variables */}
        <div
          ref={cardRef}
          style={{
            transform: `perspective(1200px) rotateX(var(--rotate-x, 0deg)) rotateY(var(--rotate-y, 0deg)) translateY(${
              isHovered ? "-3px" : "0px"
            })`,
            transition: isHovered
              ? "transform 0.08s ease-out, box-shadow 0.2s ease-out"
              : "transform 0.5s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.5s ease-out",
          }}
          className={`group rounded-3xl bg-white border border-slate-200/90 shadow-2xl shadow-slate-900/10 p-6 sm:p-8 lg:p-10 overflow-hidden relative backdrop-blur-xl ${feature.accentBorder} transition-colors will-change-transform`}
        >
          {/* Dynamic Cursor Spotlight Flashlight Effect */}
          <div
            className="pointer-events-none absolute -inset-px transition-opacity duration-300 z-0"
            style={{
              opacity: "var(--spotlight-opacity, 0)" as any,
              background: `radial-gradient(600px circle at var(--mouse-x, 50%) var(--mouse-y, 50%), ${feature.spotlightColor}, transparent 75%)`,
            }}
          />

          {/* Ambient Gradient Corner Glow */}
          <div
            className={`absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl ${feature.accentGlow} rounded-full blur-3xl pointer-events-none`}
          />

          {/* Floating Cursor Active Beacon */}
          {isHovered && (
            <div className="absolute top-4 right-6 hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900/80 text-white text-[10px] font-mono shadow-md backdrop-blur-md animate-fade-in z-20 pointer-events-none">
              <MousePointer2 className="w-3 h-3 text-indigo-400 animate-pulse" />
              <span>3D Parallax Tracking</span>
            </div>
          )}

          <div className="relative z-10 grid lg:grid-cols-12 gap-8 items-center">
            {/* Left Column: Feature Description & CTAs (7 Cols) */}
            <div className="lg:col-span-7 space-y-5">
              {/* Step & Tag Ribbon */}
              <div className="flex flex-wrap items-center gap-2.5">
                <span className="px-2.5 py-1 rounded-lg bg-slate-900 text-white font-mono text-xs font-black shadow-xs">
                  {feature.step}
                </span>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-bold border font-mono ${feature.tagColor}`}
                >
                  {feature.tag}
                </span>
              </div>

              {/* Icon & Title */}
              <div className="flex items-start gap-4">
                <div
                  className={`w-12 h-12 rounded-2xl border flex items-center justify-center shrink-0 shadow-sm transition-transform duration-300 group-hover:scale-110 ${feature.iconColor}`}
                >
                  <Icon className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight leading-tight">
                    {feature.title}
                  </h3>
                </div>
              </div>

              {/* Description */}
              <p className="text-sm sm:text-base text-slate-600 font-normal leading-relaxed">
                {feature.desc}
              </p>

              {/* Checkmark Bullets */}
              <div className="space-y-2.5 pt-1">
                {feature.bullets.map((bullet, bIdx) => (
                  <div key={bIdx} className="flex items-start gap-2.5 text-xs sm:text-sm text-slate-700">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    <span className="font-medium">{bullet}</span>
                  </div>
                ))}
              </div>

              {/* Direct Action Link Button */}
              <div className="pt-3">
                <Link
                  href={feature.linkHref}
                  className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-slate-900 hover:bg-indigo-600 text-white text-xs sm:text-sm font-bold shadow-md hover:shadow-lg hover:scale-105 active:scale-95 transition-all group/btn"
                >
                  <span>{feature.linkText}</span>
                  <ArrowRight className="w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
                </Link>
              </div>
            </div>

            {/* Right Column: High-Tech Live Visual UI Mock (5 Cols) */}
            <div className="lg:col-span-5">
              <div className="rounded-2xl border border-slate-200/90 bg-slate-50/80 p-5 shadow-inner backdrop-blur-sm">
                {feature.previewType === "chat" && (
                  <div className="space-y-3 font-sans text-xs">
                    <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                      <span className="font-bold text-slate-800 flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                        Active Buyer Session
                      </span>
                      <span className="text-[10px] font-mono text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
                        Sub-50ms Kernel
                      </span>
                    </div>
                    {/* User bubble */}
                    <div className="flex justify-end">
                      <div className="bg-indigo-600 text-white p-2.5 rounded-2xl rounded-tr-none max-w-[85%] font-medium shadow-sm">
                        Add Apple iPhone 15 to my cart
                      </div>
                    </div>
                    {/* Agent bubble */}
                    <div className="flex justify-start">
                      <div className="bg-white border border-slate-200 p-2.5 rounded-2xl rounded-tl-none max-w-[90%] shadow-2xs space-y-1.5">
                        <span className="text-slate-800 font-semibold block">
                          Added 1x Apple iPhone 15 (₹69,900.00) to cart!
                        </span>
                        <div className="p-2 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-mono flex items-center justify-between">
                          <span>🛡️ Guardian Invariants:</span>
                          <strong className="text-emerald-700">100% PASSED</strong>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {feature.previewType === "negotiate" && (
                  <div className="space-y-3 font-sans text-xs">
                    <div className="flex items-center justify-between border-b border-slate-200 pb-2 font-mono">
                      <span className="font-bold text-slate-800">A2A Bilateral RFQ</span>
                      <span className="text-[10px] text-emerald-700 font-bold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                        SETTLED • 28ms
                      </span>
                    </div>
                    {/* Margin Gauge Visual */}
                    <div className="p-3 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-2">
                      <div className="flex justify-between text-[11px] font-mono font-bold">
                        <span className="text-slate-600">Calculated Margin:</span>
                        <span className="text-emerald-700">26.8% (Safe)</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden flex">
                        <div className="bg-rose-500 w-[15%]" title="Floor (15%)" />
                        <div className="bg-amber-400 w-[10%]" title="Target (25%)" />
                        <div className="bg-emerald-500 w-[75%]" title="Surplus" />
                      </div>
                      <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                        <span>0%</span>
                        <span className="text-rose-600 font-bold">15% Floor Lock</span>
                        <span>100%</span>
                      </div>
                    </div>
                    <div className="p-2 rounded-xl bg-indigo-50/70 border border-indigo-200 text-indigo-900 text-[11px] font-mono flex items-center justify-between">
                      <span>Sweetener Lift:</span>
                      <strong className="text-indigo-700">+₹298.50 Merchant Profit</strong>
                    </div>
                  </div>
                )}

                {feature.previewType === "dashboard" && (
                  <div className="space-y-2.5 font-sans text-xs">
                    <div className="flex items-center justify-between border-b border-slate-200 pb-1.5 font-mono">
                      <span className="font-bold text-slate-800">Financial Telemetry</span>
                      <span className="text-[10px] text-indigo-700 font-bold bg-indigo-50 px-1.5 py-0.5 rounded border border-indigo-200">
                        Real SQLite Data
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="p-2.5 rounded-xl bg-white border border-slate-200 shadow-2xs">
                        <div className="text-[10px] text-slate-500 font-mono uppercase">Store Revenue</div>
                        <div className="text-base font-black text-slate-900 mt-0.5">₹1,35,129</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-white border border-slate-200 shadow-2xs">
                        <div className="text-[10px] text-slate-500 font-mono uppercase">Upsell Attach</div>
                        <div className="text-base font-black text-purple-700 mt-0.5">55.0%</div>
                      </div>
                    </div>
                    <div className="p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-mono flex items-center justify-between">
                      <span>Blocked Exploits:</span>
                      <strong className="text-emerald-700">100% Contained</strong>
                    </div>
                  </div>
                )}

                {feature.previewType === "campaigns" && (
                  <div className="space-y-3 font-sans text-xs">
                    <div className="flex items-center justify-between border-b border-slate-200 pb-1.5 font-mono">
                      <span className="font-bold text-slate-800">AI Strategy Pipeline</span>
                      <span className="text-[10px] text-amber-700 font-bold bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">
                        Rule 6 Bound
                      </span>
                    </div>
                    {/* 3 Steps */}
                    <div className="space-y-1.5">
                      <div className="p-2 rounded-lg bg-white border border-slate-200 flex items-center justify-between font-mono text-[11px]">
                        <span>1. Natural Objective</span>
                        <span className="text-emerald-600 font-bold">✓ Synthesized</span>
                      </div>
                      <div className="p-2 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-between font-mono text-[11px]">
                        <span>2. Guardian Validate</span>
                        <span className="text-emerald-700 font-bold">✓ Margin Safe</span>
                      </div>
                      <div className="p-2 rounded-lg bg-white border border-slate-200 flex items-center justify-between font-mono text-[11px]">
                        <span>3. Catalog Live</span>
                        <span className="text-indigo-600 font-bold">● Active</span>
                      </div>
                    </div>
                  </div>
                )}

                {feature.previewType === "policy" && (
                  <div className="space-y-2.5 font-sans text-xs">
                    <div className="flex items-center justify-between border-b border-slate-200 pb-1.5 font-mono">
                      <span className="font-bold text-slate-800">Guardian Guardrails</span>
                      <span className="text-[10px] text-blue-700 font-bold bg-blue-50 px-1.5 py-0.5 rounded border border-blue-200">
                        Active Matrix
                      </span>
                    </div>
                    <div className="space-y-2">
                      <div className="p-2 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-1">
                        <div className="flex justify-between text-[11px] font-mono">
                          <span className="text-slate-600">Min Gross Margin:</span>
                          <strong className="text-indigo-700">15.0%</strong>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-1.5">
                          <div className="bg-indigo-600 h-1.5 rounded-full w-[45%]" />
                        </div>
                      </div>
                      <div className="p-2 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-1">
                        <div className="flex justify-between text-[11px] font-mono">
                          <span className="text-slate-600">Max Discount Cap:</span>
                          <strong className="text-indigo-700">20.0%</strong>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-1.5">
                          <div className="bg-indigo-600 h-1.5 rounded-full w-[35%]" />
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {feature.previewType === "receipts" && (
                  <div className="space-y-2.5 font-sans text-xs">
                    <div className="flex items-center justify-between border-b border-slate-200 pb-1.5 font-mono">
                      <span className="font-bold text-slate-800">Decision Receipt #rcpt_98f4</span>
                      <span className="text-[10px] text-sky-700 font-bold bg-sky-50 px-1.5 py-0.5 rounded border border-sky-200">
                        Signed Ed25519
                      </span>
                    </div>
                    <div className="p-2.5 rounded-xl bg-slate-900 text-slate-100 font-mono text-[10px] leading-relaxed space-y-1">
                      <div className="text-slate-400">SHA-256 Merkle Root:</div>
                      <div className="text-emerald-400 truncate">
                        e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
                      </div>
                    </div>
                    <div className="p-2 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-mono flex items-center justify-between">
                      <span>Replay Verification:</span>
                      <strong className="text-emerald-700">MATCH (Zero Drift)</strong>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function StickyFeatureShowcase() {
  const [activeTab, setActiveTab] = useState(0);

  const features = [
    {
      id: "chat",
      step: "01 / 06",
      tag: "Side A • Buyer Agent Experience",
      tagColor: "bg-purple-50 text-purple-700 border-purple-200",
      accentGlow: "from-purple-500/15 via-indigo-500/10 to-transparent",
      spotlightColor: "rgba(168, 85, 247, 0.12)",
      accentBorder: "hover:border-purple-300",
      title: "Autonomous Buyer Chat & Cart",
      desc: "Converse naturally with the AI shopping agent to discover electronics, dynamically mutate cart state, receive policy-safe upsell attachments, and execute instant Razorpay checkout.",
      bullets: [
        "Zero-Hallucination Gate enforces verified catalog prices",
        "Contextual Upsell Engine attaches margin-safe companion gear",
        "State Rollback Support ('undo') with instantaneous recovery",
      ],
      linkText: "Launch Buyer Chat",
      linkHref: "/chat",
      icon: ShoppingBag,
      iconColor: "text-purple-600 bg-purple-50 border-purple-200",
      previewType: "chat",
    },
    {
      id: "negotiate",
      step: "02 / 06",
      tag: "Dual AI • Reverse Auction • Live RFQ",
      tagColor: "bg-indigo-50 text-indigo-700 border-indigo-200",
      accentGlow: "from-indigo-500/15 via-blue-500/10 to-transparent",
      spotlightColor: "rgba(99, 102, 241, 0.12)",
      accentBorder: "hover:border-indigo-300",
      title: "A2A Autonomous Negotiation Arena",
      desc: "Procurement bots submit wholesale RFQ pricing. Merchant AI calculates multi-option counter-offers with mathematical margin protection and bundle sweeteners in sub-50ms.",
      bullets: [
        "Deterministic 15% Gross Margin Floor prevents undercutting",
        "Value-Maximizer Sweeteners unlock profitable bundle trades (+₹299 lift)",
        "Standardized MCP JSON-RPC protocol for bot-to-bot commerce",
      ],
      linkText: "Enter Negotiation Arena",
      linkHref: "/negotiate",
      icon: ArrowLeftRight,
      iconColor: "text-indigo-600 bg-indigo-50 border-indigo-200",
      previewType: "negotiate",
    },
    {
      id: "dashboard",
      step: "03 / 06",
      tag: "Side B • Control Plane & Telemetry",
      tagColor: "bg-emerald-50 text-emerald-700 border-emerald-200",
      accentGlow: "from-emerald-500/15 via-teal-500/10 to-transparent",
      spotlightColor: "rgba(16, 185, 129, 0.12)",
      accentBorder: "hover:border-emerald-300",
      title: "Financial Telemetry & Revenue Stream",
      desc: "Real-time revenue telemetry aggregated dynamically from SQLite/PostgreSQL with zero hardcoded metrics. Live conversion tracking, upsell attach rates, and blocked threats.",
      bullets: [
        "Live SQL-aggregated total store revenue & active campaign gains",
        "Upsell attach conversion telemetry & basket lift tracking",
        "Instant drilldown into signed decision audit logs",
      ],
      linkText: "Open Telemetry Dashboard",
      linkHref: "/dashboard",
      icon: BarChart3,
      iconColor: "text-emerald-600 bg-emerald-50 border-emerald-200",
      previewType: "dashboard",
    },
    {
      id: "campaigns",
      step: "04 / 06",
      tag: "Side B • AI Growth Orchestrator",
      tagColor: "bg-amber-50 text-amber-700 border-amber-200",
      accentGlow: "from-amber-500/15 via-orange-500/10 to-transparent",
      spotlightColor: "rgba(245, 158, 11, 0.12)",
      accentBorder: "hover:border-amber-300",
      title: "AI Campaign Strategy Orchestrator",
      desc: "Input natural language growth targets (e.g., 'Clear inventory with 15% discount'). AI synthesizes structured promotional rules, deterministically validated by Guardian before catalog activation.",
      bullets: [
        "3-Step Lifecycle: Propose ➔ Guardian Validate ➔ Activate to Catalog",
        "Automated margin compliance check prevents unprofitable discounts",
        "Real-time budget exhaustion limits and automatic expiry",
      ],
      linkText: "Create Campaign",
      linkHref: "/campaigns",
      icon: Target,
      iconColor: "text-amber-600 bg-amber-50 border-amber-200",
      previewType: "campaigns",
    },
    {
      id: "policy",
      step: "05 / 06",
      tag: "Side B • Policy Invariant Engine",
      tagColor: "bg-blue-50 text-blue-700 border-blue-200",
      accentGlow: "from-blue-500/15 via-indigo-500/10 to-transparent",
      spotlightColor: "rgba(59, 130, 246, 0.12)",
      accentBorder: "hover:border-blue-300",
      title: "Merchant Guardian Policy & Margin Rules",
      desc: "Configure maximum discount caps, minimum gross margin floors, high-value transaction confirmation thresholds, and bundle constraints. Every checkout intent is checked in under 50 milliseconds.",
      bullets: [
        "Rule 6 Invariant Matrix: Cost floor < Final Price < Cap",
        "Single-click policy tuning with live safety margin meter",
        "100% Deterministic Python kernel (Zero LLM hallucinations)",
      ],
      linkText: "Configure Policy Limits",
      linkHref: "/policy",
      icon: ShieldCheck,
      iconColor: "text-blue-600 bg-blue-50 border-blue-200",
      previewType: "policy",
    },
    {
      id: "receipts",
      step: "06 / 06",
      tag: "Side B • Cryptographic Audit Ledger",
      tagColor: "bg-sky-50 text-sky-700 border-sky-200",
      accentGlow: "from-sky-500/15 via-cyan-500/10 to-transparent",
      spotlightColor: "rgba(14, 165, 233, 0.12)",
      accentBorder: "hover:border-sky-300",
      title: "Decision Receipts & Replay Engine",
      desc: "Every AI shopping decision and negotiated settlement mints an immutable cryptographic record with SHA-256 Merkle root and Ed25519 signature verification for bit-for-bit replayability.",
      bullets: [
        "Cryptographic proof signed with merchant private key",
        "Deterministic 1-click Replay verification engine",
        "Complete historical audit drawer with tamper-evident seal",
      ],
      linkText: "Inspect Audit Ledger",
      linkHref: "/receipts",
      icon: FileCheck,
      iconColor: "text-sky-600 bg-sky-50 border-sky-200",
      previewType: "receipts",
    },
  ];

  const scrollToFeature = (id: string, index: number) => {
    setActiveTab(index);
    const elem = document.getElementById(`feature-${id}`);
    if (elem) {
      const topPos = elem.getBoundingClientRect().top + window.pageYOffset - 110;
      window.scrollTo({ top: topPos, behavior: "smooth" });
    }
  };

  return (
    <section className="relative space-y-8 pt-4">
      {/* Section Header */}
      <div className="text-center max-w-2xl mx-auto space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-bold uppercase tracking-wider font-mono">
          <Layers className="w-3.5 h-3.5 text-indigo-600" />
          Core Capabilities
        </div>
        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 tracking-tight">
          Complete Architecture for Autonomous Commerce
        </h2>
        <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
          Scroll down to reveal the 6 core pillars of the Merchant OS—each card tracks cursor movement with dynamic 3D tilt and radial lighting.
        </p>

        {/* Interactive Quick-Jump Navigation Tabs */}
        <div className="flex flex-wrap justify-center gap-1.5 pt-3">
          {features.map((f, i) => (
            <button
              key={f.id}
              onClick={() => scrollToFeature(f.id, i)}
              className="px-3 py-1.5 rounded-xl text-xs font-bold font-mono transition-all bg-white hover:bg-indigo-50 text-slate-700 hover:text-indigo-700 border border-slate-200 shadow-2xs"
            >
              {f.step.substring(0, 2)} {f.title.split(" ")[0]}
            </button>
          ))}
        </div>
      </div>

      {/* Sticky Stacking Cards Container with 3D Cursor Movement */}
      <div className="relative pt-6 pb-20">
        {features.map((feature, idx) => (
          <InteractiveStickyCard key={feature.id} feature={feature} idx={idx} />
        ))}
      </div>
    </section>
  );
}
