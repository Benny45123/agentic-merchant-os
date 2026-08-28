"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Shield,
  ShoppingBag,
  ArrowLeftRight,
  BarChart3,
  Target,
  ShieldCheck,
  Menu,
  X,
  Search,
  Command,
} from "lucide-react";
import InteractiveRobot from "./InteractiveRobot";
import CommandPalette from "./CommandPalette";

export default function Navbar() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);

  // Global ⌘K keyboard shortcut listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setCommandPaletteOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const navItems = [
    {
      name: "Buyer Chat",
      href: "/chat",
      icon: ShoppingBag,
      tag: "AI",
    },
    {
      name: "A2A Arena",
      href: "/negotiate",
      icon: ArrowLeftRight,
      tag: "RFQ",
      highlight: true,
    },
    {
      name: "Receipts",
      href: "/receipts",
      icon: Shield,
      tag: "Audit",
    },
    {
      name: "Dashboard",
      href: "/dashboard",
      icon: BarChart3,
      tag: "Telemetry",
    },
    {
      name: "Campaigns",
      href: "/campaigns",
      icon: Target,
      tag: "Growth",
    },
    {
      name: "Policy",
      href: "/policy",
      icon: ShieldCheck,
      tag: "Rule 6",
    },
  ];

  return (
    <>
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-2xl border-b border-slate-200 shadow-xs transition-all">
        <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 gap-2 lg:gap-4 flex-nowrap">
            {/* Left: Brand Logo (Agentic Merchant OS) */}
            <div className="flex items-center space-x-2.5 shrink-0">
              <Link href="/" className="flex items-center space-x-2.5 group">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-50 via-white to-violet-50 border border-indigo-200 flex items-center justify-center shadow-xs group-hover:border-indigo-400 group-hover:scale-105 transition-all">
                  <InteractiveRobot size="sm" showSpeech={false} />
                </div>
                <div className="whitespace-nowrap">
                  <div className="flex items-center gap-1.5">
                    <span className="text-sm sm:text-base font-black tracking-tight bg-gradient-to-r from-indigo-600 via-indigo-700 to-violet-700 bg-clip-text text-transparent">
                      Agentic Merchant OS
                    </span>
                    <span className="hidden xl:inline-block px-1.5 py-0.2 rounded text-[9px] font-extrabold bg-indigo-50 text-indigo-700 border border-indigo-200 font-mono">
                      Track 01
                    </span>
                  </div>
                  <span className="text-[10px] font-bold text-slate-400 block -mt-1">
                    Deterministic Guardian
                  </span>
                </div>
              </Link>
            </div>

            {/* Center: Navigation Links in a Single Clean Line */}
            <nav className="hidden lg:flex items-center space-x-1 whitespace-nowrap flex-nowrap">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));

                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`relative flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 whitespace-nowrap ${
                      isActive
                        ? "bg-indigo-50 text-indigo-700 shadow-xs border border-indigo-200 font-bold"
                        : "text-slate-600 hover:text-slate-900 hover:bg-slate-100/80"
                    }`}
                  >
                    <Icon
                      className={`w-3.5 h-3.5 ${
                        isActive ? "text-indigo-600" : "text-slate-400"
                      }`}
                    />
                    <span>{item.name}</span>
                    {item.highlight && !isActive && (
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
                    )}
                  </Link>
                );
              })}
            </nav>

            {/* Right: Quick Jump Trigger & Guardian Status */}
            <div className="flex items-center space-x-2 shrink-0 whitespace-nowrap">
              {/* Quick Jump Search Button */}
              <button
                type="button"
                onClick={() => setCommandPaletteOpen(true)}
                className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-white border border-slate-200 hover:border-indigo-300 text-slate-600 hover:text-slate-900 text-xs transition-all shadow-2xs group"
                title="Quick Jump to any page or scenario (⌘K)"
              >
                <Search className="w-3.5 h-3.5 text-indigo-600 group-hover:scale-110 transition-transform" />
                <span className="text-xs font-semibold">Quick Jump</span>
                <kbd className="px-1.5 py-0.5 text-[9px] font-mono font-bold bg-white rounded border border-slate-200 text-slate-500 shadow-2xs">
                  ⌘K
                </kbd>
              </button>

              {/* Status Badge */}
              <div className="hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-semibold">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span>Guardian Online</span>
                <span className="font-mono text-emerald-700 text-[10px]">28ms</span>
              </div>

              {/* Mobile Quick Jump */}
              <button
                type="button"
                onClick={() => setCommandPaletteOpen(true)}
                className="sm:hidden p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 shadow-2xs"
                title="Quick Jump"
              >
                <Search className="w-4 h-4 text-indigo-600" />
              </button>

              {/* Mobile Menu Toggle */}
              <button
                type="button"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 focus:outline-none lg:hidden transition-colors"
                aria-label="Toggle navigation menu"
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t border-slate-200 bg-white px-4 pt-3 pb-5 space-y-1.5 animate-slide-down">
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                setCommandPaletteOpen(true);
              }}
              className="w-full flex items-center justify-between px-3.5 py-2.5 mb-2 rounded-xl bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700"
            >
              <div className="flex items-center gap-2">
                <Search className="w-4 h-4 text-indigo-600" />
                <span>Quick Jump Menu (⌘K)</span>
              </div>
              <kbd className="px-1.5 py-0.5 text-[10px] font-mono bg-white rounded border border-slate-200">⌘K</kbd>
            </button>

            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                    isActive
                      ? "bg-indigo-50 text-indigo-700 border border-indigo-200 font-bold"
                      : "text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`w-4 h-4 ${isActive ? "text-indigo-600" : "text-slate-400"}`} />
                    <span>{item.name}</span>
                  </div>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200 font-mono">
                    {item.tag}
                  </span>
                </Link>
              );
            })}
          </div>
        )}
      </header>

      {/* Interactive Command Palette Modal */}
      <CommandPalette isOpen={commandPaletteOpen} onClose={() => setCommandPaletteOpen(false)} />
    </>
  );
}
