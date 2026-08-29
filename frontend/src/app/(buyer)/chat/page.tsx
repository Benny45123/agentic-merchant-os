"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import {
  CartItem,
  CheckoutResponse,
  Recommendation,
  checkoutCart,
  sendChatMessage,
  verifyPayment,
  getBuyerProfile,
  sendOtp,
  verifyOtp,
  BuyerContactProfile,
} from "@/lib/api";
import {
  Send,
  Mic,
  Sparkles,
  Bot,
  User,
  ShoppingCart,
  ShieldCheck,
  ShieldAlert,
  Shield,
  CreditCard,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ArrowRight,
  RefreshCw,
  Tag,
  Award,
  Zap,
  ShoppingBag,
  ExternalLink,
  Lock,
  Radio,
  Plus,
  Trash2,
  PartyPopper,
  Check,
  Activity,
  Cpu,
  Fingerprint,
  MessageSquare,
  Scale,
  DollarSign,
  BarChart3,
} from "lucide-react";
import InteractiveRobot from "@/components/InteractiveRobot";

interface Message {
  id: string;
  sender: "user" | "agent";
  text: string;
}

function renderFormattedText(text: string) {
  const lines = text.split("\n");
  return lines.map((line, lineIdx) => {
    const parts = line.split(/(\*\*.*?\*\*|`.*?`)/g);
    return (
      <p key={lineIdx} className={lineIdx > 0 ? "mt-1.5" : ""}>
        {parts.map((part, partIdx) => {
          if (part.startsWith("**") && part.endsWith("**")) {
            return (
              <strong key={partIdx} className="font-bold text-inherit">
                {part.slice(2, -2)}
              </strong>
            );
          }
          if (part.startsWith("`") && part.endsWith("`")) {
            return (
              <code
                key={partIdx}
                className="px-1.5 py-0.5 rounded text-[11px] font-mono bg-slate-100 border border-slate-200 text-indigo-700 font-semibold"
              >
                {part.slice(1, -1)}
              </code>
            );
          }
          return part;
        })}
      </p>
    );
  });
}

export default function BuyerChatPage() {
  const [sessionId] = useState(() => `session_${Math.random().toString(36).substring(2, 9)}`);
  const [buyerId] = useState("b_001");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "m0",
      sender: "agent",
      text: "Hello! I am your AI Shopping Assistant. How can I help you today? You can search for smartphones, laptops, smartwatches, audio gear, or explore active promotional discounts.",
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
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const quickPrompts = [
    { label: "🎧 HP-001 Headphones", text: "Add AeroSound Wireless Headphones (HP-001) to my cart" },
    { label: "📱 iPhone 15 (128GB)", text: "Add Apple iPhone 15 to my cart" },
    { label: "⚡ Galaxy S24 5G", text: "Add Samsung Galaxy S24 5G to my cart" },
    { label: "💻 MacBook Air M3", text: "Add Apple MacBook Air M3 to my cart" },
    { label: "🖥️ Dell XPS 13 OLED", text: "Add Dell XPS 13 Plus to my cart" },
    { label: "⌚ Apple Watch S9", text: "Add Apple Watch Series 9 to my cart" },
    { label: "⚡ Weekend Promotions", text: "Are there any weekend campaign discounts available?" },
    { label: "🔊 Home Soundbars", text: "Show me details for AeroSound SoundBar Pro" },
  ];

  const startVoiceInput = () => {
    if (typeof window === "undefined") return;
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Voice input is not supported in this browser. Please use Chrome, Edge, or Safari.");
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = "en-IN";
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) {
          setInput(transcript);
          handleSend(transcript);
        }
      };

      recognition.onerror = (event: any) => {
        console.warn("Speech recognition error:", event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.start();
    } catch (err: any) {
      console.error("Voice recognition failed to start:", err);
      setIsListening(false);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

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

      // Auto-trigger Guardian checkout evaluation if user requested checkout
      const lower = text.toLowerCase();
      if (
        res.cart.items.length > 0 &&
        (lower.includes("checkout") ||
          lower.includes("check out") ||
          lower.includes("pay now") ||
          lower.includes("proceed to") ||
          lower.includes("complete purchase") ||
          lower.includes("do that for me"))
      ) {
        handleCheckout();
      }
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
    if (!checkoutData) return;
    const order = checkoutData.razorpay_order || {
      order_id: checkoutData.decision.razorpay_order_id || `order_sim_${checkoutData.decision.receipt_id.substring(0, 10)}`,
      amount: checkoutData.decision.final_verified_total || cart.subtotal,
      currency: "INR",
      key_id: "rzp_test_placeholder",
    };

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
        name: "Agentic Merchant Store",
        description: "Agentic Commerce Order Checkout",
        order_id: order.order_id,
        handler: async function (response: any) {
          try {
            await verifyPayment(
              response.razorpay_order_id || order.order_id,
              response.razorpay_payment_id,
              response.razorpay_signature
            );
            const receiptId = checkoutData.decision.receipt_id;
            setPaymentSuccess(receiptId);
            setCart({ items: [], subtotal: 0 });
            setCheckoutData(null);
            setMessages((prev) => [
              ...prev,
              {
                id: `paid_${Date.now()}`,
                sender: "agent",
                text: `🎉 **Payment Verified & Authorized!** Razorpay payment (\`${response.razorpay_payment_id}\`) captured. Your order receipt is immutably signed.`,
              },
            ]);
          } catch (err: any) {
            alert(`Payment verification error: ${err.message}`);
          }
        },
        prefill: {
          name: "Alex Johnson",
          email: "alex.johnson@example.com",
          contact: "9999999999",
        },
        theme: {
          color: "#4f46e5",
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
      const receiptId = checkoutData.decision.receipt_id;
      setPaymentSuccess(receiptId);
      setCart({ items: [], subtotal: 0 });
      setCheckoutData(null);
      setMessages((prev) => [
        ...prev,
        {
          id: `paid_${Date.now()}`,
          sender: "agent",
          text: `🎉 **Payment Verified & Authorized!** Test payment captured for order \`${order.order_id}\`. Your receipt is immutably signed.`,
        },
      ]);
    } catch (err: any) {
      alert(`Payment verification error: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6 pb-12 animate-fade-in">
      {/* Top Header with Animated Commerce Assistant Visualizer */}
      <div className="bg-gradient-to-r from-white via-indigo-50/40 to-white p-6 sm:p-8 rounded-3xl border border-indigo-200/90 shadow-md relative overflow-hidden space-y-6">
        {/* Soft Ambient Light Glows */}
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-indigo-100/50 rounded-full blur-3xl pointer-events-none -z-0" />
        <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-emerald-100/40 rounded-full blur-3xl pointer-events-none -z-0" />

        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 relative z-10">
          <div className="space-y-2.5 max-w-2xl">
            {/* Animated Highlighting Badges */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-indigo-600 text-white text-xs font-black uppercase tracking-wider shadow-sm shadow-indigo-500/25 animate-pulse">
                <Bot className="w-3.5 h-3.5" />
                <span>Side A • Buyer Assistant</span>
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-200" />
                <span className="font-mono text-[11px] text-indigo-100">Zero-Hallucination Gate</span>
              </span>

              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-100 text-emerald-900 border border-emerald-300 text-xs font-mono font-black shadow-2xs">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
                </span>
                <span>Guardian Active Protection</span>
              </span>

              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 border border-slate-200 text-[11px] font-mono font-bold">
                <Lock className="w-3 h-3 text-indigo-600" />
                <span>Spend Mandate Enforced</span>
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black text-slate-900 tracking-tight leading-tight">
              Autonomous{" "}
              <span className="bg-gradient-to-r from-indigo-600 via-indigo-700 to-violet-700 bg-clip-text text-transparent">
                Commerce Assistant
              </span>
            </h1>

            <p className="text-xs sm:text-sm text-slate-600 font-normal leading-relaxed">
              Converse naturally with the AI shopping agent to discover smartphones, laptops, audio gear, and accessories, receive margin-verified bundle recommendations, and checkout securely through deterministic Commerce Guardian guardrails.
            </p>
          </div>

          {/* Right Action CTAs */}
          <div className="flex flex-wrap sm:flex-nowrap items-center gap-3 shrink-0">
            <Link
              href="/negotiate"
              className="px-4 py-3 rounded-2xl border border-slate-200 text-xs font-bold text-slate-700 bg-white hover:bg-slate-50 hover:border-slate-300 transition-all shadow-sm flex items-center gap-2 group"
            >
              <Scale className="w-4 h-4 text-indigo-600 group-hover:scale-110 transition-transform" />
              <span>A2A RFQ Arena</span>
            </Link>

            <Link
              href="/receipts"
              className="px-4 py-3 rounded-2xl bg-indigo-50 hover:bg-indigo-100/80 border border-indigo-300 text-xs font-bold text-indigo-800 transition-all shadow-sm flex items-center gap-2 group"
            >
              <Shield className="w-4 h-4 text-indigo-600 group-hover:scale-110 transition-transform" />
              <span>Audit Receipts</span>
            </Link>
          </div>
        </div>

        {/* Animated Interactive Assistant Flow Ribbon */}
        <div className="relative z-10 pt-4 border-t border-indigo-100 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs bg-white/80 p-3.5 rounded-2xl border border-indigo-100/80 shadow-2xs">
          {/* Buyer Agent Node */}
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-indigo-100 text-indigo-700 border border-indigo-200 flex items-center justify-center font-bold text-base shadow-2xs">
              💬
            </div>
            <div>
              <div className="font-extrabold text-slate-900 text-xs">Buyer Conversational Input</div>
              <span className="text-[10px] text-slate-500 font-mono">Session: {sessionId.substring(0, 14)}...</span>
            </div>
          </div>

          {/* Animated Connecting Packets */}
          <div className="flex-1 max-w-xs flex items-center justify-center gap-2 px-3 py-1 bg-indigo-50/70 rounded-xl border border-indigo-100">
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping" />
            <span className="font-mono font-black text-[10px] text-indigo-800 uppercase tracking-widest">
              Sub-50ms Kernel Evaluation
            </span>
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping [animation-delay:0.3s]" />
          </div>

          {/* Guardian Node */}
          <div className="flex items-center gap-2.5">
            <div className="text-right">
              <div className="font-extrabold text-slate-900 text-xs">Commerce Guardian Gate</div>
              <span className="text-[10px] text-emerald-700 font-mono font-bold">100% Policy Bound</span>
            </div>
            <div className="w-8 h-8 rounded-xl bg-emerald-100 text-emerald-800 border border-emerald-200 flex items-center justify-center font-bold text-base shadow-2xs">
              🛡️
            </div>
          </div>
        </div>
      </div>

      {/* Main Interactive Chat & Cart Grid */}
      <div className="grid lg:grid-cols-3 gap-6 min-h-[640px] lg:h-[calc(100vh-16rem)]">
        {/* Left 2 Columns: Clean White Science Chat Stream Pane */}
        <div className="lg:col-span-2 bg-white rounded-3xl border border-slate-200 shadow-sm flex flex-col overflow-hidden">
          {/* High-Tech Clean White Chat Topbar */}
          <div className="p-4 sm:px-6 border-b border-slate-200/80 bg-gradient-to-r from-white via-indigo-50/40 to-white flex items-center justify-between">
            <div className="flex items-center gap-3">
              {/* Interactive Mini Mascot Avatar */}
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-50 via-white to-violet-50 border border-indigo-200 flex items-center justify-center shadow-md shadow-indigo-500/10 shrink-0">
                <InteractiveRobot size="sm" showSpeech={false} />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-extrabold text-sm sm:text-base text-slate-900 tracking-tight">
                    Agentic Commerce Assistant
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
                    Sub-50ms Kernel
                  </span>
                </div>
                <div className="flex items-center gap-2 text-[11px] text-slate-500">
                  <span className="flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-emerald-700 font-semibold">Guardian Protected</span>
                  </span>
                  <span>•</span>
                  <span className="font-mono text-slate-400">Zero-Hallucination Gate</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-[11px] text-slate-500 font-mono hidden sm:inline-block px-2.5 py-1 rounded-xl bg-slate-50 border border-slate-200">
                Active Session
              </span>
            </div>
          </div>

          {/* Main Clean Quick Prompts Bar */}
          <div className="px-4 py-2.5 bg-slate-50/90 border-b border-slate-100 flex items-center gap-2 overflow-x-auto no-scrollbar shadow-2xs">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider whitespace-nowrap flex items-center gap-1.5 shrink-0 font-mono">
              <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
              <span>Quick Prompts:</span>
            </span>
            {quickPrompts.map((q, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSend(q.text)}
                className="px-3 py-1.5 rounded-xl text-xs bg-white hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-300 border border-slate-200 text-slate-700 whitespace-nowrap transition-all shadow-2xs font-bold shrink-0"
              >
                {q.label}
              </button>
            ))}
          </div>

          {/* Messages Stream */}
          <div className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-4 bg-slate-50/30">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex items-start gap-3 animate-slide-up ${
                  m.sender === "user" ? "flex-row-reverse" : "flex-row"
                }`}
              >
                {/* Avatar Badge */}
                <div
                  className={`w-8 h-8 rounded-xl flex items-center justify-center text-xs shrink-0 shadow-sm ${
                    m.sender === "user"
                      ? "bg-gradient-to-tr from-indigo-600 to-violet-600 text-white"
                      : "bg-white border border-indigo-200 text-indigo-700"
                  }`}
                >
                  {m.sender === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4 text-indigo-600" />}
                </div>

                {/* Speech Bubble */}
                <div
                  className={`max-w-[82%] sm:max-w-[75%] rounded-2xl px-4 py-3 text-sm shadow-sm leading-relaxed ${
                    m.sender === "user"
                      ? "bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-tr-none shadow-indigo-500/10"
                      : "bg-white border border-slate-200 text-slate-800 rounded-tl-none shadow-2xs"
                  }`}
                >
                  <div className="text-sm font-normal">
                    {renderFormattedText(m.text)}
                  </div>
                </div>
              </div>
            ))}

            {/* Animated Quantum Thinking Indicator */}
            {loading && (
              <div className="flex items-start gap-3 animate-fade-in">
                <div className="w-8 h-8 rounded-xl bg-white border border-indigo-200 text-indigo-700 flex items-center justify-center text-xs shrink-0 shadow-2xs">
                  <Cpu className="w-4 h-4 text-indigo-600 animate-spin" style={{ animationDuration: "3s" }} />
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-none px-4 py-3 text-xs text-slate-700 flex items-center gap-2 shadow-2xs">
                  <div className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-indigo-600 animate-bounce" />
                    <span className="w-2 h-2 rounded-full bg-indigo-600 animate-bounce [animation-delay:0.2s]" />
                    <span className="w-2 h-2 rounded-full bg-indigo-600 animate-bounce [animation-delay:0.4s]" />
                  </div>
                  <span className="text-[11px] font-semibold text-slate-600">
                    AI & Guardian analyzing catalog & margin invariants...
                  </span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Bar with Voice & Science Effects */}
          <div className="p-3 sm:p-4 border-t border-slate-200 bg-white">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="flex items-center gap-2"
            >
              <div className="relative flex-1">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask questions or say 'Add HP-001 headphones'..."
                  className="w-full pl-4 pr-10 py-3 text-sm rounded-2xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all shadow-inner font-medium text-slate-800"
                />
              </div>

              {/* Voice Input Button */}
              <button
                type="button"
                onClick={startVoiceInput}
                className={`p-3 rounded-2xl border font-semibold text-sm transition-all flex items-center justify-center ${
                  isListening
                    ? "bg-rose-500 text-white border-rose-600 animate-pulse shadow-md shadow-rose-200"
                    : "bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-200"
                }`}
                title={isListening ? "Listening..." : "Click for voice input"}
              >
                {isListening ? (
                  <div className="flex items-center gap-1 px-1">
                    <span className="w-2 h-2 rounded-full bg-white animate-ping" />
                    <span className="text-xs font-bold">Listening</span>
                  </div>
                ) : (
                  <Mic className="w-5 h-5 text-slate-700" />
                )}
              </button>

              {/* Send Button */}
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-5 py-3 rounded-2xl bg-gradient-to-r from-indigo-600 via-indigo-700 to-violet-700 hover:from-indigo-500 hover:to-violet-600 disabled:opacity-50 text-white font-bold text-sm shadow-md hover:shadow-indigo-500/20 transition-all flex items-center justify-center gap-1.5"
              >
                <Send className="w-4 h-4" />
                <span className="hidden sm:inline">Send</span>
              </button>
            </form>
          </div>
        </div>

        {/* Right Column: Clean White Cart & Guardian Radar Control */}
        <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-5 flex flex-col justify-between overflow-y-auto space-y-6">
          <div>
            {/* Cart Header */}
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <ShoppingCart className="w-4 h-4 text-indigo-600" />
                <h2 className="text-base font-extrabold text-slate-900">Your Cart</h2>
              </div>
              <span className="text-xs font-mono font-bold px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                {cart.items.length} {cart.items.length === 1 ? "item" : "items"}
              </span>
            </div>

            {/* Cart Items List */}
            {cart.items.length === 0 ? (
              <div className="text-center py-10 space-y-2">
                <div className="w-12 h-12 rounded-2xl bg-slate-50 border border-slate-200 text-slate-400 flex items-center justify-center mx-auto text-xl shadow-2xs">
                  🛒
                </div>
                <p className="text-xs text-slate-600 font-semibold">Your shopping cart is empty.</p>
                <p className="text-[11px] text-slate-400">Ask the AI assistant to add headphones or soundbars.</p>
              </div>
            ) : (
              <div className="space-y-2.5 my-4">
                {cart.items.map((item) => (
                  <div
                    key={item.sku}
                    className="p-3 rounded-2xl bg-slate-50 border border-slate-200/80 text-xs flex justify-between items-center transition-all hover:border-indigo-200 hover:bg-white shadow-2xs"
                  >
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className="font-bold text-slate-900">{item.sku}</span>
                        {item.source === "upsell" && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded-md bg-amber-100 text-amber-900 font-bold">
                            Upsell
                          </span>
                        )}
                      </div>
                      <span className="text-slate-500 text-[11px]">Quantity: {item.qty}</span>
                    </div>
                    <div className="text-right">
                      <span className="font-bold text-slate-900 text-sm font-mono block">
                        ₹{((item.observed_price * item.qty) / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                      </span>
                    </div>
                  </div>
                ))}

                {/* Subtotal */}
                <div className="pt-3 border-t border-slate-100 flex justify-between items-center font-bold text-sm text-slate-900">
                  <span className="text-slate-600">Subtotal:</span>
                  <span className="text-base font-mono font-black text-slate-900">
                    ₹{(cart.subtotal / 100).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                  </span>
                </div>
              </div>
            )}

            {/* Upsell Recommendations Card */}
            {recommendations.length > 0 && (
              <div className="mt-5 pt-4 border-t border-slate-100 space-y-2.5">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                    Recommended Addons
                  </h3>
                  <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
                    Margin Verified
                  </span>
                </div>

                <div className="space-y-2">
                  {recommendations.map((rec) => (
                    <div
                      key={rec.sku}
                      className="p-3 rounded-2xl bg-gradient-to-br from-indigo-50/50 via-white to-violet-50/40 border border-indigo-100 hover:border-indigo-300 hover:shadow-md transition-all duration-200 flex items-center justify-between text-xs group"
                    >
                      <div className="pr-2 space-y-0.5">
                        <span className="font-extrabold text-indigo-950 block">{rec.sku}</span>
                        <span className="text-slate-600 text-[11px] leading-tight block">
                          {rec.reason}
                        </span>
                      </div>
                      <button
                        onClick={() => handleAddUpsell(rec.sku)}
                        className="px-3 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs whitespace-nowrap shadow-sm hover:shadow-indigo-500/20 transition-all flex items-center gap-1 shrink-0"
                      >
                        <Plus className="w-3.5 h-3.5" />
                        <span>₹{(rec.price / 100).toFixed(0)}</span>
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Checkout Intent & Guardian Verification Engine */}
          <div className="pt-4 border-t border-slate-100 space-y-4">
            {/* Checkout Button */}
            {!checkoutData && !paymentSuccess && (
              <button
                onClick={handleCheckout}
                disabled={cart.items.length === 0 || checkingOut}
                className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:opacity-50 text-white font-bold text-sm shadow-md hover:shadow-emerald-600/20 transition-all flex items-center justify-center gap-2 group"
              >
                {checkingOut ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Evaluating Commerce Guardian Rules...</span>
                  </>
                ) : (
                  <>
                    <ShieldCheck className="w-4 h-4 text-emerald-100 group-hover:scale-110 transition-transform" />
                    <span>Check Out via Commerce Guardian</span>
                  </>
                )}
              </button>
            )}

            {/* Clean White Holographic Guardian Decision Panel */}
            {checkoutData && (
              <div className="rounded-2xl bg-gradient-to-b from-indigo-50/50 via-white to-slate-50 border border-indigo-200 text-slate-900 p-4 space-y-3.5 shadow-md animate-slide-up">
                {/* Radar Scan Header */}
                <div className="flex items-center justify-between pb-2.5 border-b border-indigo-100">
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
                    <span className="font-extrabold text-xs text-slate-900">Guardian Verification</span>
                  </div>
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider ${
                      checkoutData.decision.decision === "APPROVE"
                        ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                        : checkoutData.decision.decision === "BLOCK"
                        ? "bg-rose-100 text-rose-800 border border-rose-300"
                        : "bg-amber-100 text-amber-800 border border-amber-300"
                    }`}
                  >
                    {checkoutData.decision.decision}
                  </span>
                </div>

                {/* Active Campaign Discount Badge */}
                {checkoutData.decision.final_verified_total &&
                  checkoutData.decision.final_verified_total < cart.subtotal && (
                    <div className="p-2.5 rounded-xl bg-emerald-50 border border-emerald-300 text-emerald-800 text-xs flex items-center justify-between font-bold shadow-2xs">
                      <span className="flex items-center gap-1.5">
                        <Tag className="w-3.5 h-3.5 text-emerald-600" />
                        Active Campaign Applied!
                      </span>
                      <span className="font-mono text-emerald-700 font-black">
                        Saved ₹{((cart.subtotal - checkoutData.decision.final_verified_total) / 100).toFixed(2)}
                      </span>
                    </div>
                  )}

                {/* Guardian Checks Breakdown */}
                <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                  {checkoutData.decision.checks.map((chk, i) => (
                    <div
                      key={i}
                      className="p-2 rounded-xl bg-white border border-slate-200 flex items-start gap-2 text-[11px] shadow-2xs"
                    >
                      <span className="mt-0.5">
                        {chk.passed ? (
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                        ) : (
                          <XCircle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
                        )}
                      </span>
                      <div className="flex-1">
                        <span className="font-mono font-bold text-slate-800 block">{chk.name}</span>
                        <span className="text-slate-500 text-[10px] block leading-tight">{chk.detail}</span>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Approve: Razorpay Payment CTA */}
                {checkoutData.decision.decision === "APPROVE" && !paymentSuccess && (
                  <div className="pt-2 border-t border-indigo-100">
                    <button
                      onClick={handleOpenRazorpay}
                      className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 via-indigo-700 to-violet-700 hover:from-indigo-500 hover:to-violet-600 text-white font-extrabold transition-all shadow-md hover:shadow-indigo-500/20 flex items-center justify-center gap-2 text-xs"
                    >
                      <CreditCard className="w-4 h-4" />
                      <span>Pay ₹{((checkoutData.decision.final_verified_total || 0) / 100).toFixed(2)} via Razorpay</span>
                    </button>
                  </div>
                )}

                {/* REQUIRE_CONFIRMATION: High-Value Human-in-the-Loop Confirmation */}
                {checkoutData.decision.decision === "REQUIRE_CONFIRMATION" && !paymentSuccess && (
                  <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-300 text-amber-900 space-y-2 mt-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-xs flex items-center gap-1.5 text-amber-800">
                        <AlertTriangle className="w-4 h-4 text-amber-600" />
                        High-Value Order Gate
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-mono font-bold">
                        HITL
                      </span>
                    </div>
                    <p className="text-[11px] text-amber-800 leading-relaxed font-medium">
                      Order total (<strong>₹{((checkoutData.decision.final_verified_total || cart.subtotal) / 100).toFixed(2)}</strong>) exceeds autonomous threshold. Explicit confirmation required.
                    </p>
                    <button
                      onClick={handleOpenRazorpay}
                      className="w-full py-2.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold transition-colors shadow text-xs flex items-center justify-center gap-1.5"
                    >
                      <span>👤 Confirm & Pay via Razorpay (₹{((checkoutData.decision.final_verified_total || cart.subtotal) / 100).toFixed(2)})</span>
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Clean White & Emerald Celebratory Payment Success Card */}
            {paymentSuccess && (
              <div className="animate-celebrate p-5 rounded-2xl bg-gradient-to-b from-emerald-50 via-white to-emerald-50/30 border-2 border-emerald-400 text-slate-900 text-center space-y-3 shadow-lg">
                <div className="w-12 h-12 rounded-2xl bg-emerald-100 border border-emerald-300 text-2xl flex items-center justify-center mx-auto shadow-inner text-emerald-800">
                  🎉
                </div>
                <div>
                  <h4 className="text-sm font-black text-emerald-900">Payment Verified & Authorized!</h4>
                  <p className="text-[11px] text-slate-600 mt-0.5 font-medium">
                    Your order is confirmed and immutable decision receipt generated.
                  </p>
                </div>

                <div className="pt-2 flex flex-col gap-2">
                  <Link
                    href={`/receipts/${paymentSuccess}`}
                    className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs shadow-md transition-all flex items-center justify-center gap-1.5"
                  >
                    <span>View Immutable Audit Receipt</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>

                  <button
                    onClick={() => {
                      setPaymentSuccess(null);
                      setCheckoutData(null);
                      setCart({ items: [], subtotal: 0 });
                    }}
                    className="text-[11px] text-slate-500 hover:text-slate-800 transition-colors font-medium"
                  >
                    Start New Shopping Session
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
