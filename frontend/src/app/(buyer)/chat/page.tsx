"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import {
  CartItem,
  CheckoutResponse,
  GuardianCheck,
  Recommendation,
  checkoutCart,
  sendChatMessage,
  verifyPayment,
} from "@/lib/api";

interface Message {
  id: string;
  sender: "user" | "agent";
  text: string;
}

export default function BuyerChatPage() {
  const [sessionId] = useState(() => `session_${Math.random().toString(36).substring(2, 9)}`);
  const [buyerId] = useState("b_001");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "m0",
      sender: "agent",
      text: "Hello! I am your AI Shopping Assistant for AeroSound. How can I help you today? You can ask for headphones, soundbars, or accessories.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [cart, setCart] = useState<{ items: CartItem[]; subtotal: number }>({
    items: [],
    subtotal: 0,
  });
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [checkoutData, setCheckoutData] = useState<CheckoutResponse | null>(null);
  const [checkingOut, setCheckingOut] = useState(false);
  const [paymentSuccess, setPaymentSuccess] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || input;
    if (!text.trim() || loading) return;

    const userMsg: Message = { id: `m_${Date.now()}`, sender: "user", text };
    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInput("");
    setLoading(true);

    try {
      const res = await sendChatMessage(sessionId, buyerId, text);
      setMessages((prev) => [
        ...prev,
        { id: `agent_${Date.now()}`, sender: "agent", text: res.reply },
      ]);
      setCart(res.cart);
      setRecommendations(res.recommendations || []);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { id: `err_${Date.now()}`, sender: "agent", text: `Error: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddUpsell = (sku: string) => {
    handleSend(`Please add ${sku} to my cart`);
  };

  const handleCheckout = async () => {
    if (cart.items.length === 0 || checkingOut) return;
    setCheckingOut(true);
    setPaymentSuccess(null);

    try {
      const res = await checkoutCart(sessionId, buyerId);
      setCheckoutData(res);
    } catch (err: any) {
      alert(`Checkout failed: ${err.message}`);
    } finally {
      setCheckingOut(false);
    }
  };

  const handleOpenRazorpay = async () => {
    if (!checkoutData?.razorpay_order) return;
    const order = checkoutData.razorpay_order;

    // Check if Razorpay JS SDK is loaded and real test key is configured
    if (
      typeof (window as any).Razorpay !== "undefined" &&
      order.key_id &&
      !order.key_id.startsWith("rzp_test_placeholder")
    ) {
      const options = {
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        name: "AeroSound Store",
        description: "Agentic Commerce Order Checkout",
        order_id: order.order_id,
        handler: async function (response: any) {
          try {
            await verifyPayment(
              response.razorpay_order_id || order.order_id,
              response.razorpay_payment_id,
              response.razorpay_signature
            );
            setPaymentSuccess(checkoutData.decision.receipt_id);
          } catch (err: any) {
            alert(`Payment verification error: ${err.message}`);
          }
        },
        prefill: {
          name: "Demo Buyer",
          email: "buyer@example.com",
          contact: "9876543210",
        },
        theme: {
          color: "#4F46E5",
        },
        modal: {
          ondismiss: function () {
            console.log("Razorpay checkout modal closed by user");
          },
        },
      };

      try {
        const rzp = new (window as any).Razorpay(options);
        rzp.on("payment.failed", function (response: any) {
          alert(`Payment failed: ${response.error.description}`);
        });
        rzp.open();
        return;
      } catch (e) {
        console.warn("Razorpay popup launch failed, falling back to simulated payment:", e);
      }
    }

    // Direct simulated payment fallback for local/offline testing
    try {
      await verifyPayment(
        order.order_id,
        `pay_sim_${order.order_id.substring(10)}`,
        "mock_signature_test"
      );
      setPaymentSuccess(checkoutData.decision.receipt_id);
    } catch (err: any) {
      alert(`Payment verification error: ${err.message}`);
    }
  };

  return (
    <div className="grid lg:grid-cols-3 gap-6 h-[calc(100vh-8rem)]">
      {/* Left 2 Columns: Chat Stream */}
      <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col overflow-hidden">
        <div className="p-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-semibold text-slate-800 text-sm">AeroSound AI Assistant</span>
          </div>
          <span className="text-xs text-slate-500 font-mono">Session: {sessionId}</span>
        </div>

        {/* Messages */}
        <div className="flex-1 p-4 overflow-y-auto space-y-4">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex ${m.sender === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm ${
                  m.sender === "user"
                    ? "bg-indigo-600 text-white rounded-br-none"
                    : "bg-slate-100 text-slate-900 rounded-bl-none"
                }`}
              >
                <div className="whitespace-pre-line leading-relaxed">{m.text}</div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-slate-100 rounded-2xl rounded-bl-none px-4 py-2.5 text-sm text-slate-500 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce" />
                <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce [animation-delay:0.2s]" />
                <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce [animation-delay:0.4s]" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-3 border-t border-slate-200 bg-white">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask for products, add to cart (e.g. 'Add HP-001 headphones')..."
              className="flex-1 px-4 py-2.5 text-sm rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-medium text-sm transition-colors"
            >
              Send
            </button>
          </form>
        </div>
      </div>

      {/* Right Column: Cart & Live Guardian Control */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 flex flex-col justify-between overflow-y-auto">
        <div>
          <h2 className="text-base font-bold text-slate-900 mb-3 flex items-center justify-between">
            <span>🛒 Your Cart</span>
            <span className="text-xs px-2 py-0.5 rounded bg-slate-100 font-mono text-slate-600">
              {cart.items.length} items
            </span>
          </h2>

          {cart.items.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-xs">
              Cart is currently empty.
            </div>
          ) : (
            <div className="space-y-2 mb-4">
              {cart.items.map((item) => (
                <div
                  key={item.sku}
                  className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs flex justify-between items-center"
                >
                  <div>
                    <span className="font-semibold text-slate-800 block">{item.sku}</span>
                    <span className="text-slate-500">Qty: {item.qty}</span>
                    {item.source === "upsell" && (
                      <span className="ml-2 text-[10px] px-1.5 py-0.2 rounded bg-amber-100 text-amber-800 font-medium">
                        Upsell
                      </span>
                    )}
                  </div>
                  <span className="font-semibold text-slate-900">
                    ₹{((item.observed_price * item.qty) / 100).toFixed(2)}
                  </span>
                </div>
              ))}

              <div className="pt-3 border-t border-slate-200 flex justify-between font-bold text-sm text-slate-900">
                <span>Subtotal:</span>
                <span>₹{(cart.subtotal / 100).toFixed(2)}</span>
              </div>
            </div>
          )}

          {/* Upsell Recommendations */}
          {recommendations.length > 0 && (
            <div className="mt-4 pt-3 border-t border-slate-100">
              <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                💡 Recommended Addons (Margin Safe)
              </h3>
              <div className="space-y-2">
                {recommendations.map((rec) => (
                  <div
                    key={rec.sku}
                    className="p-2.5 rounded-xl bg-indigo-50/50 border border-indigo-100 flex items-center justify-between text-xs"
                  >
                    <div className="pr-2">
                      <span className="font-bold text-indigo-900 block">{rec.sku}</span>
                      <span className="text-slate-600 text-[11px] leading-tight block">
                        {rec.reason}
                      </span>
                    </div>
                    <button
                      onClick={() => handleAddUpsell(rec.sku)}
                      className="px-2.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-xs whitespace-nowrap transition-colors"
                    >
                      + Add ₹{(rec.price / 100).toFixed(0)}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Checkout & Guardian Evaluation Modal */}
        <div className="mt-6 pt-4 border-t border-slate-200">
          <button
            onClick={handleCheckout}
            disabled={cart.items.length === 0 || checkingOut}
            className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-bold text-sm shadow transition-colors flex items-center justify-center gap-2"
          >
            {checkingOut ? (
              <span>Evaluating Guardian Rules...</span>
            ) : (
              <span>🛡️ Check Out via Commerce Guardian</span>
            )}
          </button>

          {/* Guardian Decision Panel */}
          {checkoutData && (
            <div className="mt-4 p-3 rounded-xl bg-slate-900 text-white text-xs space-y-2">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <span className="font-bold">Guardian Result:</span>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-extrabold ${
                    checkoutData.decision.decision === "APPROVE"
                      ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                      : checkoutData.decision.decision === "BLOCK"
                      ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                      : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                  }`}
                >
                  {checkoutData.decision.decision}
                </span>
              </div>

              {/* Render Visible Checks List */}
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {checkoutData.decision.checks.map((chk, i) => (
                  <div key={i} className="flex items-start gap-1.5 text-[11px]">
                    <span>{chk.passed ? "✅" : "❌"}</span>
                    <div className="flex-1">
                      <span className="font-mono text-slate-300">{chk.name}</span>
                      <span className="text-slate-400 block text-[10px]">{chk.detail}</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pay or Confirm Button */}
              {checkoutData.decision.decision === "APPROVE" && !paymentSuccess && (
                <div className="pt-2 border-t border-slate-800">
                  <button
                    onClick={handleOpenRazorpay}
                    className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold transition-colors shadow flex items-center justify-center gap-2 text-xs"
                  >
                    💳 Open Razorpay Checkout (₹{((checkoutData.decision.final_verified_total || 0) / 100).toFixed(2)})
                  </button>
                </div>
              )}

              {paymentSuccess && (
                <div className="pt-2 border-t border-emerald-800 text-emerald-400 font-bold text-center">
                  🎉 Payment Completed!
                  <Link
                    href={`/receipts/${paymentSuccess}`}
                    className="block mt-1 text-xs text-indigo-400 hover:underline"
                  >
                    View Immutable Decision Receipt &rarr;
                  </Link>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
