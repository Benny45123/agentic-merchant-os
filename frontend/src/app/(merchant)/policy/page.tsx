"use client";

import { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";

export default function PolicyEditorPage() {
  const [merchantId] = useState("m_001");
  const [policy, setPolicy] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    fetchApi<any>(`/policy?merchant_id=${merchantId}`)
      .then(setPolicy)
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
          allowed_products_for_discount: policy.allowed_products_for_discount,
          minimum_stock_to_sell: Number(policy.minimum_stock_to_sell),
        }),
      });
      setPolicy(updated);
      setSaveSuccess(true);
    } catch (err: any) {
      alert(`Policy update failed: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="text-center py-20 text-slate-500">Loading merchant policy...</div>;
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5">
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-600">
              Deterministic Guardrail Control
            </span>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-slate-100 text-slate-700">
              Policy v{policy?.version || 1}
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900">Merchant Policy Constraints</h1>
          <p className="text-sm text-slate-600">
            Configure hard financial rules. Every policy save creates an immutable versioned record without corrupting historical receipt audits.
          </p>
        </div>

        {saveSuccess && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold rounded-xl">
            ✅ Policy updated to Version {policy?.version}! Guardian will enforce these new rules immediately.
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="font-bold text-slate-700 block mb-1">
              Maximum Allowed Discount (%)
            </label>
            <input
              type="number"
              value={policy?.maximum_discount_pct || 0}
              onChange={(e) => setPolicy({ ...policy, maximum_discount_pct: e.target.value })}
              min="0"
              max="100"
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500"
            />
            <span className="text-[11px] text-slate-500 block mt-0.5">
              Guardian will BLOCK any buyer or campaign discount higher than this.
            </span>
          </div>

          <div>
            <label className="font-bold text-slate-700 block mb-1">
              Minimum Required Margin (%)
            </label>
            <input
              type="number"
              value={policy?.minimum_margin_pct || 0}
              onChange={(e) => setPolicy({ ...policy, minimum_margin_pct: e.target.value })}
              min="0"
              max="100"
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500"
            />
            <span className="text-[11px] text-slate-500 block mt-0.5">
              Computed as (Price_after_discount - Cost) / Price_after_discount.
            </span>
          </div>

          <div>
            <label className="font-bold text-slate-700 block mb-1">
              Maximum Order Value Ceiling (paise)
            </label>
            <input
              type="number"
              value={policy?.maximum_order_value || 0}
              onChange={(e) => setPolicy({ ...policy, maximum_order_value: e.target.value })}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500"
            />
            <span className="text-[11px] text-slate-500 block mt-0.5">
              Current: ₹{((policy?.maximum_order_value || 0) / 100).toFixed(2)}
            </span>
          </div>

          <div>
            <label className="font-bold text-slate-700 block mb-1">
              Minimum Stock Reserve to Sell
            </label>
            <input
              type="number"
              value={policy?.minimum_stock_to_sell || 0}
              onChange={(e) => setPolicy({ ...policy, minimum_stock_to_sell: e.target.value })}
              min="0"
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500"
            />
            <span className="text-[11px] text-slate-500 block mt-0.5">
              Prevents inventory from dropping below this threshold on checkout.
            </span>
          </div>

          <div className="pt-3 border-t border-slate-100">
            <button
              type="submit"
              disabled={saving}
              className="w-full py-3 rounded-xl bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white font-bold text-sm shadow transition-colors"
            >
              {saving ? "Creating Versioned Policy..." : "Save Policy (Creates New Version)"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
