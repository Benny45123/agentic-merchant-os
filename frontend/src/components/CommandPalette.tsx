"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  Shield,
  ShoppingBag,
  ArrowLeftRight,
  BarChart3,
  Target,
  ShieldCheck,
  Zap,
  Play,
  RotateCcw,
  Sparkles,
  Command,
  X,
  ExternalLink,
} from "lucide-react";

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);

  const actions = [
    {
      category: "Navigation",
      items: [
        {
          id: "nav-chat",
          title: "Buyer Assistant Chat",
          description: "Conversational shopping with margin-safe upsells",
          icon: ShoppingBag,
          href: "/chat",
          badge: "Buyer AI",
        },
        {
          id: "nav-negotiate",
          title: "A2A Dynamic RFQ Arena",
          description: "Autonomous bilateral multi-turn negotiation",
          icon: ArrowLeftRight,
          href: "/negotiate",
          badge: "Dynamic Pricing",
        },
        {
          id: "nav-dashboard",
          title: "Merchant Telemetry Dashboard",
          description: "Live revenue, upsell attach rate, audit stats",
          icon: BarChart3,
          href: "/dashboard",
          badge: "Telemetry",
        },
        {
          id: "nav-campaigns",
          title: "AI Campaign Orchestrator",
          description: "Natural language campaign goal to verified promotion",
          icon: Target,
          href: "/campaigns",
          badge: "Growth Engine",
        },
        {
          id: "nav-policy",
          title: "Merchant Policy Control",
          description: "Deterministic margin floors and discount caps",
          icon: ShieldCheck,
          href: "/policy",
          badge: "Rule 6",
        },
        {
          id: "nav-receipts",
          title: "Decision Receipts Explorer",
          description: "Immutable cryptographic audit trail & replay ledger",
          icon: Shield,
          href: "/receipts",
          badge: "Ed25519 Signed",
        },
      ],
    },
    {
      category: "Interactive Demos",
      items: [
        {
          id: "demo-a2a",
          title: "Launch Autonomous RFQ Scenario",
          description: "Simulate 3x AeroSound HP-001 with bundle sweetener",
          icon: Zap,
          href: "/negotiate",
          badge: "Demo 7",
        },
        {
          id: "demo-chat-promo",
          title: "Test Active Campaign Discount in Chat",
          description: "Add promotional headphones and view savings badge",
          icon: Sparkles,
          href: "/chat",
          badge: "Demo 4",
        },
        {
          id: "demo-policy-test",
          title: "Adjust Policy Safety Margin",
          description: "Change max discount and test Guardian blocking",
          icon: Shield,
          href: "/policy",
          badge: "Demo 3",
        },
      ],
    },
  ];

  const allItems = actions.flatMap((group) => group.items);
  const filteredItems = query.trim()
    ? allItems.filter(
        (item) =>
          item.title.toLowerCase().includes(query.toLowerCase()) ||
          item.description.toLowerCase().includes(query.toLowerCase()) ||
          item.badge.toLowerCase().includes(query.toLowerCase())
      )
    : allItems;

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === "Escape") {
        onClose();
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % filteredItems.length);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filteredItems.length) % filteredItems.length);
      } else if (e.key === "Enter" && filteredItems[selectedIndex]) {
        e.preventDefault();
        handleSelect(filteredItems[selectedIndex]);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, filteredItems, selectedIndex]);

  const handleSelect = (item: (typeof allItems)[0]) => {
    router.push(item.href);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity animate-fade-in"
        onClick={onClose}
      />

      {/* Modal Container */}
      <div className="relative w-full max-w-2xl bg-white border border-slate-200 rounded-2xl shadow-2xl overflow-hidden backdrop-blur-2xl z-10 animate-slide-down">
        {/* Search Bar Input */}
        <div className="flex items-center px-4 border-b border-slate-100 bg-white">
          <Search className="w-5 h-5 text-indigo-600 mr-3" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search commands, pages, demo scenarios, receipts... (Press Esc to exit)"
            className="w-full py-4 bg-transparent text-sm text-slate-800 placeholder-slate-400 focus:outline-none font-medium"
            autoFocus
          />
          {query && (
            <button onClick={() => setQuery("")} className="p-1 text-slate-400 hover:text-slate-600">
              <X className="w-4 h-4" />
            </button>
          )}
          <kbd className="hidden sm:inline-block ml-2 px-2 py-0.5 text-[10px] font-mono font-semibold text-slate-500 bg-slate-100 rounded border border-slate-200">
            ESC
          </kbd>
        </div>

        {/* Results List */}
        <div className="max-h-96 overflow-y-auto p-2 divide-y divide-slate-100">
          {filteredItems.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-xs">
              No matching actions found for &ldquo;{query}&rdquo;
            </div>
          ) : (
            <div className="space-y-1 py-1">
              {filteredItems.map((item, idx) => {
                const Icon = item.icon;
                const isSelected = idx === selectedIndex;

                return (
                  <button
                    key={item.id}
                    onClick={() => handleSelect(item)}
                    onMouseEnter={() => setSelectedIndex(idx)}
                    className={`w-full flex items-center justify-between px-3.5 py-3 rounded-xl text-left transition-all ${
                      isSelected
                        ? "bg-indigo-50/80 border border-indigo-200 text-indigo-900"
                        : "text-slate-700 hover:bg-slate-50"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                          isSelected ? "bg-indigo-600 text-white shadow-sm shadow-indigo-500/20" : "bg-slate-100 text-slate-500"
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="font-semibold text-xs text-slate-900 flex items-center gap-2">
                          <span>{item.title}</span>
                          <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-slate-100 border border-slate-200 text-indigo-700">
                            {item.badge}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-500">{item.description}</p>
                      </div>
                    </div>

                    <div className="flex items-center text-slate-400 text-xs">
                      {isSelected && (
                        <span className="text-[10px] font-mono text-indigo-600 mr-2 flex items-center gap-1 font-semibold">
                          Jump <ExternalLink className="w-3 h-3" />
                        </span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer shortcuts */}
        <div className="px-4 py-2.5 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
          <div className="flex items-center gap-3 font-mono">
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-white rounded text-[10px] border border-slate-200 shadow-2xs">↑</kbd>
              <kbd className="px-1.5 py-0.5 bg-white rounded text-[10px] border border-slate-200 shadow-2xs">↓</kbd> navigate
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-white rounded text-[10px] border border-slate-200 shadow-2xs">↵</kbd> select
            </span>
          </div>
          <span className="text-slate-400">Agentic Merchant OS • Sub-50ms Kernel</span>
        </div>
      </div>
    </div>
  );
}
