import Link from "next/link";
import { ShieldCheck, Cpu, Lock, Terminal, Sparkles } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-white/80 backdrop-blur-md border-t border-slate-200/80 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-6">
          {/* Brand & Track info */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center space-x-2">
              <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center text-white">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <span className="font-bold text-slate-900 text-sm tracking-tight">
                Agentic Merchant OS
              </span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
                Track 01
              </span>
            </div>
            <p className="text-xs text-slate-500 max-w-md leading-relaxed">
              Deterministic Commerce Guardian & AI Agentic Commerce Platform. Engineered for zero-hallucination policy enforcement, margin lockouts, autonomous RFQ negotiation, and immutable cryptographic receipts.
            </p>
            <div className="flex items-center gap-3 text-[11px] text-slate-500 font-medium">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                Rule 6 Engine Active
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Lock className="w-3 h-3 text-indigo-500" />
                Ed25519 Replay Verification
              </span>
            </div>
          </div>

          {/* Quick Nav Links */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-3">
              Platform Links
            </h4>
            <ul className="space-y-2 text-xs text-slate-600">
              <li>
                <Link href="/chat" className="hover:text-indigo-600 transition-colors">
                  🛍️ Buyer Agent Chat & Cart
                </Link>
              </li>
              <li>
                <Link href="/negotiate" className="hover:text-indigo-600 transition-colors">
                  🤝 Autonomous A2A Arena
                </Link>
              </li>
              <li>
                <Link href="/dashboard" className="hover:text-indigo-600 transition-colors">
                  📊 Merchant Revenue Telemetry
                </Link>
              </li>
              <li>
                <Link href="/campaigns" className="hover:text-indigo-600 transition-colors">
                  🎯 AI Campaign Orchestrator
                </Link>
              </li>
              <li>
                <Link href="/policy" className="hover:text-indigo-600 transition-colors">
                  🛡️ Commerce Guardian Policy
                </Link>
              </li>
            </ul>
          </div>

          {/* Technology Stack & Security */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-3">
              Architecture
            </h4>
            <div className="flex flex-wrap gap-1.5">
              <span className="px-2 py-1 bg-slate-100 rounded-md text-[10px] font-mono text-slate-700 font-medium">
                Next.js 14 App Router
              </span>
              <span className="px-2 py-1 bg-slate-100 rounded-md text-[10px] font-mono text-slate-700 font-medium">
                Tailwind CSS 3
              </span>
              <span className="px-2 py-1 bg-slate-100 rounded-md text-[10px] font-mono text-slate-700 font-medium">
                FastAPI Kernel
              </span>
              <span className="px-2 py-1 bg-indigo-50 text-indigo-700 border border-indigo-200 rounded-md text-[10px] font-mono font-medium">
                Razorpay Checkout
              </span>
              <span className="px-2 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-md text-[10px] font-mono font-medium">
                Rule 6 Guard Kernel
              </span>
            </div>
          </div>
        </div>

        <div className="pt-6 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-400">
          <div>
            © {new Date().getFullYear()} Agentic Merchant OS. Razorpay Buildathon Track 01 Submission.
          </div>
          <div className="flex items-center gap-4 text-[11px]">
            <span>Deterministic Sandbox: <strong className="text-slate-700">m_001</strong></span>
            <span>Latency Floor: <strong className="text-emerald-600">&lt; 50ms</strong></span>
          </div>
        </div>
      </div>
    </footer>
  );
}
