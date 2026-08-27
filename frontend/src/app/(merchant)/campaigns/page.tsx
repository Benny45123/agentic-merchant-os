"use client";

import { useState } from "react";
import {
  CampaignProposalData,
  activateCampaign,
  proposeCampaign,
} from "@/lib/api";

export default function CampaignsPage() {
  const [merchantId] = useState("m_001");
  const [objective, setObjective] = useState("Increase sales of wireless headphones this weekend");
  const [loading, setLoading] = useState(false);
  const [proposal, setProposal] = useState<CampaignProposalData | null>(null);
  const [activated, setActivated] = useState<string | null>(null);

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
    if (!proposal) return;
    try {
      const res = await activateCampaign(proposal.proposal_id);
      setActivated(res.campaign_id);
    } catch (err: any) {
      alert(`Activation failed: ${err.message}`);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-indigo-600 block mb-1">
            Side B — AI Growth Engine
          </span>
          <h1 className="text-2xl font-extrabold text-slate-900">Campaign Strategy Orchestrator</h1>
          <p className="text-sm text-slate-600">
            State your revenue objective in natural language. The AI will propose a bounded promotional offer, which is then deterministically verified by the Guardian against your margin and budget policies before activation.
          </p>
        </div>

        {/* Objective Input */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-700 uppercase tracking-wider block">
            Merchant Revenue Objective
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              placeholder="e.g. Boost audio accessories attach rate with 10% discount..."
              className="flex-1 px-4 py-2.5 text-sm rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
            <button
              onClick={handlePropose}
              disabled={loading || !objective.trim()}
              className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-bold text-sm shadow transition-colors"
            >
              {loading ? "Orchestrating..." : "Propose Campaign"}
            </button>
          </div>
        </div>
      </div>

      {/* Proposal Review Card */}
      {proposal && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h2 className="text-base font-bold text-slate-900">AI Generated Proposal Review</h2>
            <span
              className={`text-xs px-2.5 py-0.5 rounded-full font-bold uppercase ${
                proposal.guardian_decision.decision === "APPROVE"
                  ? "bg-emerald-100 text-emerald-800"
                  : proposal.guardian_decision.decision === "BLOCK"
                  ? "bg-rose-100 text-rose-800"
                  : "bg-amber-100 text-amber-800"
              }`}
            >
              Guardian: {proposal.guardian_decision.decision}
            </span>
          </div>

          <div className="grid sm:grid-cols-3 gap-4">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs">
              <span className="text-slate-500 block mb-0.5">Proposed Discount</span>
              <span className="text-lg font-bold text-indigo-600">{proposal.discount_pct}% OFF</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs">
              <span className="text-slate-500 block mb-0.5">Campaign Budget</span>
              <span className="text-lg font-bold text-slate-900">₹{(proposal.budget / 100).toFixed(2)}</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs">
              <span className="text-slate-500 block mb-0.5">Eligible SKUs</span>
              <span className="text-sm font-mono font-bold text-slate-800">{proposal.eligible_skus.join(", ")}</span>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1">
            <span className="font-bold text-slate-700">AI Rationale:</span>
            <p className="text-slate-600 leading-relaxed">{proposal.rationale}</p>
          </div>

          {/* Guardian Checks Breakdown */}
          <div className="space-y-1.5 text-xs">
            <span className="font-bold text-slate-700 block">Guardian Validation Breakdown:</span>
            {proposal.guardian_decision.checks.map((chk, i) => (
              <div key={i} className="flex items-start gap-1.5 text-[11px]">
                <span>{chk.passed ? "✅" : "❌"}</span>
                <div>
                  <span className="font-mono font-bold text-slate-800">{chk.name}</span>
                  <span className="text-slate-500 block">{chk.detail}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Activate Button */}
          {proposal.guardian_decision.decision !== "BLOCK" && !activated && (
            <div className="pt-3 border-t border-slate-100">
              <button
                onClick={handleActivate}
                className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow transition-colors"
              >
                🚀 Confirm & Activate Campaign to Catalog
              </button>
            </div>
          )}

          {activated && (
            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold text-center">
              🎉 Campaign is LIVE! Static discount offer rows have been written to the catalog.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
