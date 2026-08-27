#!/usr/bin/env python3
"""
End-to-End Scenario Suite Runner for Agentic Merchant OS
Runs all 6 demo scenarios sequentially against local stack.
"""

import sys
from pathlib import Path

# Add scripts directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import scenario_happy_path
import scenario_injection_attack
import scenario_price_change
import scenario_campaign_lifecycle
import demo_uap_agent_buyer
import scenario_insufficient_autopay_funds


def main() -> int:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    print("\n==================================================================")
    print(f"🚀 RUNNING ALL 6 END-TO-END DEMO SCENARIOS against {base_url}")
    print("==================================================================")

    results = []

    # Scenario 1: Happy Path Purchase
    s1 = scenario_happy_path.run_scenario(base_url)
    results.append(("Scenario 1: Happy Path Purchase", s1))

    # Scenario 2: Prompt Injection Defense
    s2 = scenario_injection_attack.run_scenario(base_url)
    results.append(("Scenario 2: Catalog Prompt Injection Defense", s2))

    # Scenario 3: Price Drift Mid-Flow Detection
    s3 = scenario_price_change.run_scenario(base_url)
    results.append(("Scenario 3: Price Drift Mid-Flow Detection", s3))

    # Scenario 4: Campaign Orchestrator Lifecycle
    s4 = scenario_campaign_lifecycle.run_scenario(base_url)
    results.append(("Scenario 4: Campaign Orchestrator Lifecycle", s4))

    # Scenario 5: Autonomous A2A Machine Purchase (UAP / MCP Protocol)
    s5 = demo_uap_agent_buyer.run_scenario(base_url)
    results.append(("Scenario 5: Autonomous A2A Machine Purchase (UAP/MCP)", s5))

    # Scenario 6: Insufficient Autopay Funds & Mandate Cap Breach
    s6 = scenario_insufficient_autopay_funds.run_scenario(base_url)
    results.append(("Scenario 6: Insufficient Autopay Funds / Mandate Breach", s6))

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
        print("🎉 ALL 6 DEMO SCENARIOS COMPLETED SUCCESSFULLY WITH 100% PASS RATE!")
        return 0
    else:
        print("❌ ONE OR MORE SCENARIOS FAILED.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
