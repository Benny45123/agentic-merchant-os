# Changelog

All notable changes to the Agentic Merchant OS platform are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and adheres to Semantic Versioning.

---

## [1.2.0] - 2026-08-30
### Added
- **Universal Extensionless CLI Wrappers (`bin/`)**: Created unified entrypoints (`setup_env`, `start`, `stop`, `test`, `simulate_ai_buyer`, `logs`, `run_scenarios`) enabling single-command execution on macOS, Linux, and Git Bash.
- **Native Windows Batch (`*.bat`) & PowerShell (`*.ps1`) Scripts**: Added dedicated scripts in `bin/` (`setup_env.bat`, `start.bat`, `stop.bat`, `test.bat`, `simulate_ai_buyer.bat`, `start.ps1`, `stop.ps1`) for zero-WSL Windows compatibility.
- **Root-Level Model Context Protocol (MCP) Config (`.mcp.json`)**: Configured automatic MCP tool discovery for **Claude Code CLI** (`claude`) and **Claude Desktop**.
- **Comprehensive Cross-Platform Documentation**: Updated `README.md` with a detailed command matrix and descriptions across macOS, Linux, and Windows.

---

## [1.1.0] - 2026-08-29
### Added
- **Headless Autonomous AI Buyer CLI Simulator (`scripts/simulate_ai_buyer.py` & `bin/simulate_ai_buyer.sh`)**:
  - Implemented machine-to-machine (A2A) wholesale procurement over Universal Agent Protocol (UAP-1.0) and MCP.
  - Added autonomous catalog discovery, B2B RFQ proposal formulation, margin-safe counter-offer analysis, and Guardian settlement in < 1.5 seconds.
- **Interactive Cryptographic Merkle Proof Tree Visualizer (`frontend/src/components/MerkleTreeVisualizer.tsx`)**:
  - Rendered a visual 3-leaf Merkle Tree ($H_{cart} \parallel H_{policy} \parallel H_{sig} \rightarrow H_{root}$) on Decision Receipts detail page (`/receipts/[id]`).
  - Added animated SVG branch lines, 1-click hash copy buttons, and live bit-for-bit zero-drift Replay verification.
- **100% Offline Zero-LLM Fallback Engine (`backend/app/ai_provider/`)**:
  - Built `ResilientMultiProvider` cascading across Groq (Qwen/Llama), Google Gemini (3.5 Flash-Lite), OpenRouter, and an offline deterministic mock.
  - Ensures zero 500 errors and zero HTTP 429 rate limit disruptions even under network drops.
- **Architectural Specifications & Tasks**:
  - Created `docs/21_AI_BUYER_SIMULATOR_AND_MERKLE_PROOFS.md`, `agent_tasks/agent_16_ai_buyer_simulator.md`, `agent_tasks/agent_17_merkle_tree_visualizer.md`, `agent_tasks/agent_18_offline_zero_llm_resilience.md`.

### Fixed
- **3D Parallax Sticky Showcase Jitter (`StickyFeatureShowcase.tsx`)**: Decoupled stationary container measurement from GPU CSS variables (`--rotate-x`, `--rotate-y`) running at 120 FPS.
- **Seed Policy Thresholds (`seed.py`)**: Restored canonical thresholds for 100% Pytest pass rate (47/47 passing).

---

## [1.0.0] - 2026-08-28
### Added
- **Conversational Buyer Chat & Checkout UI (`/chat`)**:
  - Built real-time shopping chat powered by LangGraph with natural language search, cart mutations, voice input, and companion upsells.
  - Integrated state rollback (`undo` command) and seamless Razorpay test-mode checkout modal.
- **Bilateral A2A Reverse Auction & Negotiation Arena (`/negotiate`)**:
  - Interactive Dynamic Margin Gauge with animated color-shifting based on Rule 6 margin floor ($\ge 15.0\%$).
  - Bilateral dialogue feed with merchant counter-offers and companion bundle sweeteners (+₹298.50 profit lift).
- **AI Campaign Strategy Orchestrator (`/campaigns`)**:
  - 3-step lifecycle: Objective-to-Proposal LLM synthesis $\rightarrow$ Guardian Policy Validation $\rightarrow$ Live Catalog Promotion Activation.
- **Live Financial Telemetry Dashboard (`/dashboard`)**:
  - Real SQL-aggregated metric cards (Store Revenue, Upsell Conversion, Campaign Lift, Blocked Attacks).
  - Searchable Decision Receipts audit table with live refresh.
- **Merchant Policy Control Center (`/policy`)**:
  - Interactive policy editor enforcing Rule 6 Gross Margin Floor ($\ge 15\%$) and order caps.
- **Deterministic Commerce Guardian Kernel (`backend/app/guardian/`)**:
  - Compiled 22-invariant pure Python validation kernel executing in sub-50ms with zero LLM on the payment authorization path.
- **Cryptographic Decision Receipts Ledger (`backend/app/receipts/`)**:
  - Immutable audit trail generation with Ed25519 digital signatures and SHA-256 Merkle root hashing.
  - Bit-for-bit zero-drift Replay Engine (`/receipts/[id]/replay`).
- **Prompt Injection & Adversarial Security Classifier (`backend/app/security/classifier.py`)**:
  - Sub-5ms heuristic regex scanner blocking role overrides and jailbreak exploits (`ADMIN_OVERRIDE_100`).
- **Automated End-to-End Demo Scenario Test Suite (`tests/scenario_*.py`)**:
  - Built 8 automated scenario scripts testing happy path, injection defense, price drift, underpayment tampering, campaign lifecycle, UAP checkout, autopay breach, and A2A reverse auction.

---

## [0.1.0] - 2026-08-27
### Added
- **Repository Architecture Foundation**:
  - Initial directory skeleton per `02_SYSTEM_ARCHITECTURE.md`.
  - SQLAlchemy 2.0 async database models for all entities (`05_DATA_MODEL.md`).
  - Async database engine, SQLite WAL configuration, and Alembic migrations.
  - Core domain enums (`DecisionType`, `CampaignStatus`, `CampaignEventType`, `OrderStatus`, `OfferType`).
  - JWT authentication and mandate validation dependencies (`04_API_CONTRACTS.md`).
  - Idempotent seed script (`app/seed.py`) with electronics catalog fixtures and malicious injection test items.
  - Architectural Import Graph Linter (`scripts/check_import_graph.py`) mechanically preventing LLMs from importing payment adapters.
  - Environment templates (`.env.example` and `frontend/.env.local.example`).
