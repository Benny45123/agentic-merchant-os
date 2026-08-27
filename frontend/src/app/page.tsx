import Link from "next/link";

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto py-12 px-4 text-center">
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-semibold uppercase tracking-wider mb-6">
        Razorpay Buildathon Track 01
      </div>
      <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight mb-4">
        AI Growth & Agentic Commerce OS
      </h1>
      <p className="text-lg text-slate-600 max-w-2xl mx-auto mb-10 leading-relaxed">
        Agent-readable merchant catalog shopped by AI buyers, gated by a deterministic 
        <strong className="text-slate-900"> Commerce Guardian</strong> with immutable 
        <strong className="text-slate-900"> Decision Receipts</strong>, margin-safe upsells, and an AI Campaign Orchestrator.
      </p>

      <div className="grid sm:grid-cols-2 gap-6 text-left">
        <Link
          href="/chat"
          className="group block p-6 bg-white rounded-2xl border border-slate-200 hover:border-indigo-500 hover:shadow-lg transition-all"
        >
          <div className="w-12 h-12 rounded-xl bg-indigo-100 flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform">
            🛍️
          </div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">Buyer Agent & Checkout</h2>
          <p className="text-sm text-slate-600 mb-4">
            Experience conversational commerce, automated cart construction, policy-safe upsells, and live Guardian evaluation.
          </p>
          <span className="text-sm font-semibold text-indigo-600 flex items-center gap-1">
            Launch Buyer Chat &rarr;
          </span>
        </Link>

        <Link
          href="/dashboard"
          className="group block p-6 bg-white rounded-2xl border border-slate-200 hover:border-indigo-500 hover:shadow-lg transition-all"
        >
          <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center text-2xl mb-4 group-hover:scale-110 transition-transform">
            📊
          </div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">Merchant Control Plane</h2>
          <p className="text-sm text-slate-600 mb-4">
            Live revenue aggregations (zero hardcoded numbers), receipt audit viewer with replay engine, and campaign orchestrator.
          </p>
          <span className="text-sm font-semibold text-emerald-600 flex items-center gap-1">
            Open Merchant Dashboard &rarr;
          </span>
        </Link>
      </div>
    </div>
  );
}
