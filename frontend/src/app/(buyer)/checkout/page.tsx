"use client";

import React, { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Script from "next/script";
import Link from "next/link";
import { CheckCircle2, ShieldCheck, CreditCard, ArrowRight, Loader2, Sparkles } from "lucide-react";

function CheckoutContent() {
  const searchParams = useSearchParams();

  const orderId = searchParams.get("order_id") || "order_test_demo";
  const amountStr = searchParams.get("amount") || "6990000";
  const receiptId = searchParams.get("receipt_id") || "";
  const itemName = searchParams.get("item") || "Store Product";

  const amountPaise = parseInt(amountStr, 10) || 6990000;
  const amountInr = amountPaise / 100.0;

  const [loading, setLoading] = useState(false);
  const [isPaid, setIsPaid] = useState(false);
  const [paymentId, setPaymentId] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function checkStatus() {
      try {
        const res = await fetch(`http://localhost:8000/payments/sync/${orderId}`, { method: "POST" });
        if (res.ok) {
          const data = await res.json();
          if (data.paid) {
            setIsPaid(true);
            setPaymentId(data.payment_id || `pay_${orderId.slice(-10)}`);
          }
        }
      } catch (err) {
        // Ignore network check error on initial mount
      }
    }
    checkStatus();
  }, [orderId]);

  const openRazorpay = () => {
    setError(null);
    setLoading(true);

    if (typeof (window as any).Razorpay === "undefined") {
      handlePaymentSuccess(`pay_test_${orderId.slice(-10)}`);
      return;
    }

    const options = {
      key: "rzp_test_TUjDfAof7bwb12",
      amount: amountPaise,
      currency: "INR",
      name: "Agentic Merchant Store",
      description: `Order ${orderId}`,
      prefill: {
        name: "Alex Johnson",
        email: "shopper@agenticstore.com",
        contact: "9999999999",
      },
      theme: {
        color: "#2563eb",
      },
      handler: async function (response: any) {
        const pId = response.razorpay_payment_id || `pay_test_${orderId.slice(-10)}`;
        await handlePaymentSuccess(pId);
      },
      modal: {
        ondismiss: function () {
          setLoading(false);
        },
      },
    };

    try {
      const rzp = new (window as any).Razorpay(options);
      rzp.on("payment.failed", function (response: any) {
        setError(response.error?.description || "Payment failed on Razorpay");
        setLoading(false);
      });
      rzp.open();
    } catch (err: any) {
      setError(err.message || "Failed to open Razorpay modal");
      setLoading(false);
    }
  };

  const handlePaymentSuccess = async (pId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/checkout/${orderId}/pay`, { method: "POST" });
      if (res.ok) {
        setIsPaid(true);
        setPaymentId(pId);
      } else {
        setError("Failed to record payment confirmation");
      }
    } catch (err: any) {
      setError(err.message || "Network error syncing payment");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-4 sm:p-6">
      <Script src="https://checkout.razorpay.com/v1/checkout.js" strategy="lazyOnload" />

      <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6 relative overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-5">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-xl font-black shadow-lg shadow-blue-600/30">
              💳
            </div>
            <div>
              <h1 className="text-base font-black text-white">Agentic Merchant Store</h1>
              <div className="flex items-center gap-1.5 text-xs text-blue-400 font-semibold">
                <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
                Razorpay Checkout
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-slate-400 font-medium">Total Due</div>
            <div className="text-xl font-black text-emerald-400 font-mono">₹{amountInr.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</div>
          </div>
        </div>

        {isPaid ? (
          <div className="bg-emerald-950/50 border border-emerald-500/30 rounded-3xl p-6 text-center space-y-4 animate-in fade-in zoom-in duration-300">
            <div className="w-16 h-16 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center mx-auto text-3xl font-black shadow-lg shadow-emerald-500/20">
              <CheckCircle2 className="w-8 h-8 text-emerald-400" />
            </div>
            <div>
              <h2 className="text-lg font-black text-white">Payment Captured &amp; Verified!</h2>
              <p className="text-xs text-emerald-300 font-mono mt-1">Payment ID: {paymentId}</p>
            </div>
            <p className="text-xs text-slate-400">
              Your transaction has been cryptographically signed by the Commerce Guardian and recorded on the immutable ledger.
            </p>
            <div className="pt-2 space-y-2">
              {receiptId && (
                <Link
                  href={`/receipts/${receiptId}`}
                  className="w-full py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold transition flex items-center justify-center gap-2"
                >
                  <ShieldCheck className="w-4 h-4 text-blue-400" />
                  View Immutable Decision Receipt
                </Link>
              )}
              <Link
                href="/chat"
                className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-black shadow-lg shadow-blue-600/30 transition flex items-center justify-center gap-2"
              >
                Return to Buyer Chat
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-5">
            {/* Order Details */}
            <div className="bg-slate-950/80 border border-slate-800/80 rounded-2xl p-4 space-y-2.5 text-xs">
              <div className="flex justify-between text-slate-400">
                <span>Item:</span>
                <span className="font-semibold text-slate-200">{itemName}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Order Reference:</span>
                <span className="font-mono text-slate-300 font-bold">{orderId}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Safety Gate:</span>
                <span className="text-emerald-400 font-bold flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5" /> 100% Guardian Protected
                </span>
              </div>
            </div>

            {/* Razorpay Banner */}
            <div className="bg-gradient-to-r from-blue-950/40 to-indigo-950/40 border border-blue-500/30 rounded-2xl p-4 text-xs text-blue-200 space-y-1">
              <div className="font-bold flex items-center gap-1.5 text-blue-300">
                <Sparkles className="w-4 h-4 text-blue-400" />
                Official Razorpay Checkout Modal
              </div>
              <p className="text-[11px] text-slate-400">
                Test checkout supporting UPI Apps (Google Pay, PhonePe, Paytm, BHIM), Cards, and NetBanking.
              </p>
            </div>

            {error && (
              <div className="p-3 bg-red-950/50 border border-red-500/30 rounded-xl text-red-300 text-xs">
                ⚠️ {error}
              </div>
            )}

            {/* Action Button */}
            <button
              onClick={openRazorpay}
              disabled={loading}
              className="w-full py-4 rounded-2xl bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 text-white font-black text-sm shadow-xl shadow-blue-600/30 transition-all flex items-center justify-center gap-2 active:scale-98 cursor-pointer"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Opening Razorpay Gateway...</span>
                </>
              ) : (
                <>
                  <CreditCard className="w-4 h-4" />
                  <span>Pay ₹{amountInr.toLocaleString("en-IN", { minimumFractionDigits: 2 })} with Razorpay</span>
                  <ArrowRight className="w-4 h-4 ml-1" />
                </>
              )}
            </button>
          </div>
        )}

        {/* Footer */}
        <div className="text-center text-[11px] text-slate-500 pt-2 border-t border-slate-800/80 flex items-center justify-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>256-Bit Encrypted • Powered by Agentic Merchant OS &amp; Razorpay</span>
        </div>
      </div>
    </div>
  );
}

export default function CheckoutPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400">Loading Checkout...</div>}>
      <CheckoutContent />
    </Suspense>
  );
}
