#!/usr/bin/env python3
"""
End-to-End Scenario Suite Runner for Agentic Merchant OS
Runs all 8 success, failure, attack, and edge-case demo scenarios sequentially against local stack.
"""

import sys
from pathlib import Path

# Add scripts directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import scenario_happy_path
import scenario_injection_attack
import scenario_price_change
import scenario_price_tamper_attack
import scenario_campaign_lifecycle
import demo_uap_agent_buyer
import scenario_insufficient_autopay_funds
import scenario_a2a_negotiation
import scenario_telegram_gateway
import scenario_headless_autopay
import scenario_google_ap2_mandates


def main() -> int:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    print("\n==================================================================")
    print(f"🚀 RUNNING ALL 11 END-TO-END SCENARIOS & EDGE CASES against {base_url}")
    print("==================================================================")

    results = []

    # Scenario 1: Happy Path Purchase (Success)
    s1 = scenario_happy_path.run_scenario(base_url)
    results.append(("Scenario 1: Happy Path Purchase & Upsell Attach", s1))

    # Scenario 2: Prompt Injection Defense (Adversarial Attack)
    s2 = scenario_injection_attack.run_scenario(base_url)
    results.append(("Scenario 2: Catalog Prompt Injection Defense", s2))

    # Scenario 3: Price Drift Mid-Flow Detection (Dynamic Edge Case)
    s3 = scenario_price_change.run_scenario(base_url)
    results.append(("Scenario 3: Price Drift Mid-Flow Detection", s3))

    # Scenario 4: Price Tampering & Underpayment Attack (Adversarial Exploit)
    s4 = scenario_price_tamper_attack.run_scenario(base_url)
    results.append(("Scenario 4: Price Tampering & Underpayment Attack", s4))

    # Scenario 5: Campaign Orchestrator Lifecycle (Merchant Growth)
    s5 = scenario_campaign_lifecycle.run_scenario(base_url)
    results.append(("Scenario 5: Campaign Orchestrator Lifecycle & Attribution", s5))

    # Scenario 6: Autonomous A2A Machine Purchase (UAP / MCP Protocol)
    s6 = demo_uap_agent_buyer.run_scenario(base_url)
    results.append(("Scenario 6: Autonomous A2A Machine Purchase (UAP/MCP)", s6))

    # Scenario 7: Insufficient Autopay Funds & Mandate Cap Breach (Failure Guardrail)
    s7 = scenario_insufficient_autopay_funds.run_scenario(base_url)
    results.append(("Scenario 7: Insufficient Autopay Funds & Mandate Breach", s7))

    # Scenario 8: Autonomous A2A Dynamic Negotiation (Reverse Auction & Margin Floor)
    s8 = scenario_a2a_negotiation.run_scenario(base_url)
    results.append(("Scenario 8: Autonomous A2A Dynamic Negotiation (Reverse Auction)", s8))

    # Scenario 9: Omnichannel Telegram Bot Mobile Gateway (Direct Buy, Reverse Auction, Payment Sync)
    s9 = scenario_telegram_gateway.run_scenario(base_url)
    results.append(("Scenario 9: Omnichannel Telegram Bot Mobile Gateway", s9))

    # Scenario 10: Autonomous Headless Razorpay UPI AutoPay (tok_rzp_autopay_...)
    s10 = scenario_headless_autopay.run_scenario(base_url)
    results.append(("Scenario 10: Headless Razorpay UPI AutoPay (0-Click)", s10))

    # Scenario 11: Google AP2 Open vs. Closed Mandate Chains (ES256 & Cart Digest Defense)
    s11 = scenario_google_ap2_mandates.run_scenario(base_url)
    results.append(("Scenario 11: Google AP2 Mandate Chains & Cart Digest Defense", s11))

    print("\n==================================================================")
    print("📋 SUMMARY RESULTS:")
    print("==================================================================")
    all_passed = True
    for name, passed in results:
        status_icon = "✅ PASSED" if passed else "❌ FAILED"
        if not passed:
            all_passed = False
        print(f"  • {name}: {status_icon}")

    print("==================================================================")
    if all_passed:
        print("🎉 ALL 11 SCENARIOS & EDGE CASES COMPLETED SUCCESSFULLY WITH 100% PASS RATE!")
        return 0
    else:
        print("❌ ONE OR MORE SCENARIOS FAILED.")
        return 1




if __name__ == "__main__":
    sys.exit(main())
