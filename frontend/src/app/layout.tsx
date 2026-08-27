import type { Metadata } from "next";
import Link from "next/link";
import Script from "next/script";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agentic Merchant OS",
  description: "Deterministic Guardian & AI Agentic Commerce Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <Script
          src="https://checkout.razorpay.com/v1/checkout.js"
          strategy="lazyOnload"
        />
      </head>
      <body className="bg-slate-50 min-h-screen text-slate-900 flex flex-col font-sans">
        <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">
                Agentic Merchant OS
              </span>
              <span className="text-xs px-2.5 py-0.5 rounded-full font-medium bg-indigo-50 text-indigo-700 border border-indigo-200">
                Track 01
              </span>
            </div>

            <nav className="flex items-center space-x-6 text-sm font-medium">
              <Link href="/chat" className="text-slate-600 hover:text-indigo-600 transition-colors">
                🛍️ Buyer Chat
              </Link>
              <Link href="/dashboard" className="text-slate-600 hover:text-indigo-600 transition-colors">
                📊 Merchant Dashboard
              </Link>
              <Link href="/campaigns" className="text-slate-600 hover:text-indigo-600 transition-colors">
                🎯 Campaigns
              </Link>
              <Link href="/policy" className="text-slate-600 hover:text-indigo-600 transition-colors">
                🛡️ Policy Editor
              </Link>
            </nav>
          </div>
        </header>

        <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
          {children}
        </main>

        <footer className="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-500">
          Razorpay Buildathon Track 01 — Deterministic Commerce Guardian & Agentic OS
        </footer>
      </body>
    </html>
  );
}
