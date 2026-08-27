"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ReceiptData, getReceipt, replayReceipt } from "@/lib/api";

export default function ReceiptDetailPage() {
  const params = useParams();
  const receiptId = params.id as string;

  const [receipt, setReceipt] = useState<ReceiptData | null>(null);
  const [loading, setLoading] = useState(true);
  const [replayResult, setReplayResult] = useState<any>(null);
  const [replaying, setReplaying] = useState(false);

  useEffect(() => {
    if (!receiptId) return;
    getReceipt(receiptId)
      .then(setReceipt)
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [receiptId]);

  const handleReplay = async () => {
    if (replaying) return;
    setReplaying(true);
    try {
      const res = await replayReceipt(receiptId);
      setReplayResult(res);
    } catch (err: any) {
      alert(`Replay failed: ${err.message}`);
    } finally {
      setReplaying(false);
    }
  };

  if (loading) {
    return <div className="text-center py-20 text-slate-500">Loading audit receipt...</div>;
  }

  if (!receipt) {
    return (
      <div className="text-center py-20 text-slate-500">
        Receipt not found. <Link href="/chat" className="text-indigo-600 underline">Return to shop</Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider bg-slate-100 text-slate-700">
              Immutable Decision Receipt
            </span>
            <span
              className={`text-xs px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                receipt.decision === "APPROVE"
                  ? "bg-emerald-100 text-emerald-800"
                  : receipt.decision === "BLOCK"
                  ? "bg-rose-100 text-rose-800"
                  : "bg-amber-100 text-amber-800"
              }`}
            >
              {receipt.decision}
            </span>
          </div>
          <h1 className="text-xl font-mono font-bold text-slate-900">{receipt.receipt_id}</h1>
          <span className="text-xs text-slate-500">
            Recorded at: {new Date(receipt.created_at).toUTCString()}
          </span>
        </div>

        <button
          onClick={handleReplay}
          disabled={replaying}
          className="px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white font-semibold text-xs transition-colors flex items-center gap-1.5"
        >
          {replaying ? "Replaying Checks..." : "🔄 Replay Deterministic Checks"}
        </button>
      </div>

      {/* Replay Result Banner */}
      {replayResult && (
        <div className="p-4 rounded-2xl bg-slate-900 text-white border border-slate-700 space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-bold text-sm">Deterministic Audit Verification</span>
            <span
              className={`px-2.5 py-0.5 rounded text-xs font-bold ${
                replayResult.matches_original
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                  : "bg-rose-500/20 text-rose-400"
              }`}
            >
              {replayResult.matches_original ? "✅ 100% MATCH VERIFIED" : "❌ MISMATCH BUG"}
            </span>
          </div>
          <p className="text-xs text-slate-300">
            Re-evaluated {replayResult.replayed_checks.length} checks against the frozen snapshots inside this receipt. Replay Decision: <strong>{replayResult.replay_decision}</strong>.
          </p>
        </div>
      )}

      {/* Timeline Section */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Left: Snapshotted Intent Items */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
            📦 Frozen Cart Items Snapshot
          </h2>
          <div className="space-y-2">
            {receipt.items_snapshot.map((item: any, i: number) => (
              <div
                key={i}
                className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs flex justify-between"
              >
                <div>
                  <span className="font-bold text-slate-800 block">{item.sku}</span>
                  <span className="text-slate-500">Qty: {item.qty} | Cat: {item.category || "audio"}</span>
                </div>
                <span className="font-mono font-bold text-slate-900">
                  ₹{((item.authoritative_price || item.observed_price) * item.qty / 100).toFixed(2)}
                </span>
              </div>
            ))}
          </div>

          <div className="pt-3 border-t border-slate-100 flex justify-between text-sm font-bold text-slate-900">
            <span>Verified Total:</span>
            <span>₹{((receipt.final_verified_total || receipt.observed_total) / 100).toFixed(2)}</span>
          </div>
        </div>

        {/* Right: Guardian Verification Checklist */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
            🛡️ Guardian Verification Audit
          </h2>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {receipt.guardian_checks.map((chk: any, i: number) => (
              <div
                key={i}
                className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs flex items-start gap-2"
              >
                <span>{chk.passed ? "✅" : "❌"}</span>
                <div>
                  <span className="font-mono font-bold text-slate-800 block">{chk.name}</span>
                  <span className="text-slate-500 text-[11px]">{chk.detail}</span>
                </div>
              </div>
            ))}
          </div>

          {receipt.razorpay_order_id && (
            <div className="pt-3 border-t border-slate-100 text-xs space-y-1 font-mono text-slate-600">
              <div>Razorpay Order: {receipt.razorpay_order_id}</div>
              {receipt.razorpay_payment_id && (
                <div className="text-emerald-700 font-bold">
                  Payment Captured: {receipt.razorpay_payment_id}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
