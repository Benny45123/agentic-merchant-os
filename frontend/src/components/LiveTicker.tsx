"use client";

import { useEffect, useState } from "react";
import { ShieldCheck, Zap, ArrowLeftRight, CheckCircle2, ShieldAlert, Sparkles, Activity } from "lucide-react";

export default function LiveTicker() {
  const [tickerIndex, setTickerIndex] = useState(0);

  const tickerEvents = [
    {
      icon: ShieldAlert,
      tag: "14ms • DEFENSE",
      tagColor: "bg-rose-100 text-rose-800 border-rose-200",
      text: "Blocked adversarial prompt injection (ADMIN_OVERRIDE_100) — Cost floor intact",
      time: "Just now",
    },
    {
      icon: ArrowLeftRight,
      tag: "28ms • A2A RFQ",
      tagColor: "bg-indigo-100 text-indigo-800 border-indigo-200",
      text: "Bilateral negotiation settled for 3x HP-001 @ ₹4,239.65 (+₹418.95 lift)",
      time: "12s ago",
    },
    {
      icon: Sparkles,
      tag: "18ms • PROMOTION",
      tagColor: "bg-emerald-100 text-emerald-800 border-emerald-200",
      text: "Active Weekend Campaign applied 10% discount on Wireless Tech & Earbuds (Saved ₹299.90)",
      time: "24s ago",
    },
    {
      icon: ShieldCheck,
      tag: "32ms • AUDIT",
      tagColor: "bg-sky-100 text-sky-800 border-sky-200",
      text: "Decision Receipt #rcpt_98f4e2 signed with SHA-256 Merkle root & Ed25519 key",
      time: "48s ago",
    },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setTickerIndex((prev) => (prev + 1) % tickerEvents.length);
    }, 4500);

    return () => clearInterval(interval);
  }, [tickerEvents.length]);

  const current = tickerEvents[tickerIndex];

  return (
    <div className="bg-slate-50/95 border-b border-slate-200/90 px-4 py-1.5 text-xs text-slate-600 overflow-hidden">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Left Live Pulse */}
        <div className="flex items-center gap-2 shrink-0 font-mono text-[11px] text-slate-500">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="font-bold text-slate-700">LIVE GUARDIAN AUDIT FEED</span>
        </div>

        {/* Center Animated Event Carousel */}
        <div className="flex-1 overflow-hidden flex items-center justify-center">
          <div key={tickerIndex} className="flex items-center gap-2 animate-slide-up text-[11px]">
            <span className={`px-2 py-0.5 rounded-full font-mono font-bold text-[10px] border ${current.tagColor}`}>
              {current.tag}
            </span>
            <span className="text-slate-800 font-medium truncate max-w-md sm:max-w-xl">{current.text}</span>
          </div>
        </div>

        {/* Right Telemetry Chip */}
        <div className="hidden sm:flex items-center gap-2 shrink-0 font-mono text-[10px] text-slate-500">
          <span className="text-emerald-600 font-semibold">● 100% Deterministic</span>
          <span className="text-slate-300">|</span>
          <span className="text-indigo-600 font-semibold">Rule 6 Lock</span>
        </div>
      </div>
    </div>
  );
}
