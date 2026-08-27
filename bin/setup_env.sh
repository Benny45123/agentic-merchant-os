#!/usr/bin/env bash
# ==============================================================================
# Agentic Merchant OS - Setup Script (uv prioritized, fallback to manual venv)
# Strict Python 3.12 / 3.11 Enforced + Auto JWT Secret Key Generation
# + Step-by-Step API Provider Key Assistant (Gemini, Groq, OpenRouter, Razorpay)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=================================================================="
echo "🚀 Setting up Agentic Merchant OS on host system..."
echo "📁 Repository Root: $REPO_ROOT"
echo "=================================================================="

cd "$REPO_ROOT/backend"

# Ensure backend .env exists
if [ ! -f ".env" ]; then
    echo "📄 Creating backend/.env from .env.example..."
    cp "$REPO_ROOT/.env.example" "$REPO_ROOT/backend/.env"
fi

# ------------------------------------------------------------------------------
# Auto-Generate Secure JWT Signing Key (if placeholder or empty)
# ------------------------------------------------------------------------------
CURRENT_JWT_KEY=$(grep "^JWT_SIGNING_KEY=" .env | cut -d '=' -f2- || true)
if [ -z "$CURRENT_JWT_KEY" ] || [[ "$CURRENT_JWT_KEY" == *"change_this"* ]] || [[ "$CURRENT_JWT_KEY" == *"your_jwt"* ]] || [ ${#CURRENT_JWT_KEY} -lt 32 ]; then
    echo "🔑 Generating secure random 64-character JWT Signing Key..."
    if command -v openssl >/dev/null 2>&1; then
        RAND_KEY=$(openssl rand -hex 32)
    else
        RAND_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || date +%s%N | sha256sum | head -c 64)
    fi

    # Update .env
    if grep -q "^JWT_SIGNING_KEY=" .env; then
        sed -i.bak "s|^JWT_SIGNING_KEY=.*|JWT_SIGNING_KEY=$RAND_KEY|" .env && rm -f .env.bak
    else
        echo "JWT_SIGNING_KEY=$RAND_KEY" >> .env
    fi
    echo "✅ JWT Signing Key injected into backend/.env"
fi

# ------------------------------------------------------------------------------
# STEP 1: Attempt UV Setup First (Fast & Modern)
# ------------------------------------------------------------------------------
USE_UV=false

if command -v uv >/dev/null 2>&1; then
    echo "⚡ Found 'uv' package manager! Attempting setup with uv (Python 3.12/3.11)..."
    
    # Try Python 3.12 first, then 3.11
    if uv venv .venv --python 3.12 2>/dev/null; then
        echo "✅ uv created .venv with Python 3.12"
        USE_UV=true
    elif uv venv .venv --python 3.11 2>/dev/null; then
        echo "✅ uv created .venv with Python 3.11"
        USE_UV=true
    else
        echo "⚠️ uv could not locate Python 3.12 or 3.11 directly. Falling back to manual locator..."
    fi

    if [ "$USE_UV" = true ]; then
        source .venv/bin/activate
        echo "📦 Installing backend packages via uv pip..."
        uv pip install -r requirements.txt
    fi
fi

# ------------------------------------------------------------------------------
# STEP 2: Fallback to Manual Python 3.12 / 3.11 Locator if uv was not used
# ------------------------------------------------------------------------------
if [ "$USE_UV" = false ]; then
    echo "🔍 Using standard Python 3.12 / 3.11 locator..."

    CANDIDATE_PATHS=(
        "python3.12"
        "python3.11"
        "/opt/homebrew/bin/python3.12"
        "/opt/homebrew/bin/python3.11"
        "/usr/local/bin/python3.12"
        "/usr/local/bin/python3.11"
        "$HOME/.pyenv/shims/python3.12"
        "$HOME/.pyenv/shims/python3.11"
        "$HOME/.local/bin/python3.12"
    )

    PYTHON_BIN=""
    for candidate in "${CANDIDATE_PATHS[@]}"; do
        if command -v "$candidate" >/dev/null 2>&1; then
            PY_VER=$("$candidate" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || true)
            if [ "$PY_VER" = "3.12" ] || [ "$PY_VER" = "3.11" ]; then
                PYTHON_BIN="$candidate"
                echo "✅ Selected stable Python: $PYTHON_BIN (v$PY_VER)"
                break
            fi
        fi
    done

    if [ -z "$PYTHON_BIN" ]; then
        echo "❌ ERROR: Python 3.12 or 3.11 is required, but was not found!"
        echo "   (Detected default python3 is incompatible or 3.14+)"
        echo ""
        echo "👉 If using uv, run: uv python install 3.12"
        echo "   Or via Homebrew: brew install python@3.12"
        echo ""
        echo "   Then re-run: ./bin/setup_env.sh"
        exit 1
    fi

    # Create venv manually
    if [ -d ".venv" ]; then
        VENV_PY_VER=$(.venv/bin/python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "incompatible")
        if [ "$VENV_PY_VER" != "3.12" ] && [ "$VENV_PY_VER" != "3.11" ]; then
            echo "🔄 Recreating .venv (existing venv version was $VENV_PY_VER)..."
            rm -rf .venv
        fi
    fi

    if [ ! -d ".venv" ]; then
        "$PYTHON_BIN" -m venv .venv
        echo "✅ Created .venv using $PYTHON_BIN"
    fi

    source .venv/bin/activate
    echo "📦 Installing backend packages via pip..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# ------------------------------------------------------------------------------
# STEP 3: Run Database Migrations & Idempotent Seed
# ------------------------------------------------------------------------------
echo ""
echo "🗄️ [3/5] Running database migrations and idempotent seed..."
alembic upgrade head
python -m app.seed

# ------------------------------------------------------------------------------
# STEP 4: Setup Frontend Dependencies
# ------------------------------------------------------------------------------
echo ""
echo "💻 [4/5] Setting up frontend dependencies..."
cd "$REPO_ROOT/frontend"

if [ ! -f ".env.local" ]; then
    echo "📄 Creating frontend/.env.local from .env.local.example..."
    cp .env.local.example .env.local
fi

if command -v npm >/dev/null 2>&1; then
    echo "📦 Installing Node.js packages..."
    npm install
else
    echo "⚠️ npm not found on host. Please ensure Node.js (v20+) is installed to run the frontend."
fi

# ------------------------------------------------------------------------------
# STEP 5: Step-by-Step API Provider Setup & Credentials Assistant
# ------------------------------------------------------------------------------
echo ""
echo "=================================================================="
echo "🌐 [5/5] Step-by-Step API Provider Setup Wizard"
echo "=================================================================="
echo "Configure your AI Model & Payment keys (or press Enter to keep defaults)."
echo ""

# Helper to open URL in default browser
open_url() {
    local target_url="$1"
    if command -v open >/dev/null 2>&1; then
        open "$target_url"
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$target_url" >/dev/null 2>&1 || true
    fi
}

# Helper to update a key in backend/.env
set_env_key() {
    local key="$1"
    local value="$2"
    local env_file="$REPO_ROOT/backend/.env"
    if grep -q "^$key=" "$env_file"; then
        sed -i.bak "s|^$key=.*|$key=$value|" "$env_file" && rm -f "$env_file.bak"
    else
        echo "$key=$value" >> "$env_file"
    fi
}

if [ -t 0 ]; then
    # --------------------------------------------------------------------------
    # 5.1 Google Gemini API Key
    # --------------------------------------------------------------------------
    echo "------------------------------------------------------------------"
    echo "🌟 [1/4] Google Gemini Provider (Primary Model)"
    echo "Portal: https://aistudio.google.com/app/apikey"
    read -p "👉 Open Google AI Studio in browser? [y/N]: " OPEN_GEMINI || true
    if [[ "$OPEN_GEMINI" =~ ^[Yy]$ ]]; then
        echo "🚀 Opening Google AI Studio..."
        open_url "https://aistudio.google.com/app/apikey"
    fi
    read -p "📝 Paste GEMINI_API_KEY (press Enter to skip): " USER_GEMINI || true
    if [ -n "$USER_GEMINI" ]; then
        set_env_key "GEMINI_API_KEY" "$USER_GEMINI"
        set_env_key "LLM_PROVIDER" "gemini"
        echo "   ✅ Saved GEMINI_API_KEY to backend/.env"
    fi
    echo ""

    # --------------------------------------------------------------------------
    # 5.2 Groq Cloud API Key
    # --------------------------------------------------------------------------
    echo "------------------------------------------------------------------"
    echo "⚡ [2/4] Groq Cloud Provider (Free Limits: qwen/qwen3.8-27b, llama-3.3-70b)"
    echo "Portal: https://console.groq.com/keys"
    read -p "👉 Open Groq Console in browser? [y/N]: " OPEN_GROQ || true
    if [[ "$OPEN_GROQ" =~ ^[Yy]$ ]]; then
        echo "🚀 Opening Groq Cloud Console..."
        open_url "https://console.groq.com/keys"
    fi
    read -p "📝 Paste GROQ_API_KEY (press Enter to skip): " USER_GROQ || true
    if [ -n "$USER_GROQ" ]; then
        set_env_key "GROQ_API_KEY" "$USER_GROQ"
        set_env_key "GROQ_MODEL" "qwen/qwen3.8-27b"
        read -p "👉 Set Groq as your active LLM provider (LLM_PROVIDER=groq)? [y/N]: " SET_GROQ_ACTIVE || true
        if [[ "$SET_GROQ_ACTIVE" =~ ^[Yy]$ ]]; then
            set_env_key "LLM_PROVIDER" "groq"
            echo "   ✅ Set LLM_PROVIDER=groq with model qwen/qwen3.8-27b"
        fi
        echo "   ✅ Saved GROQ_API_KEY to backend/.env"
    fi
    echo ""

    # --------------------------------------------------------------------------
    # 5.3 OpenRouter API Key
    # --------------------------------------------------------------------------
    echo "------------------------------------------------------------------"
    echo "🔀 [3/4] OpenRouter Provider (Free Community Models: Llama 3.3 70B, DeepSeek)"
    echo "Portal: https://openrouter.ai/keys"
    read -p "👉 Open OpenRouter Keys page in browser? [y/N]: " OPEN_OR || true
    if [[ "$OPEN_OR" =~ ^[Yy]$ ]]; then
        echo "🚀 Opening OpenRouter..."
        open_url "https://openrouter.ai/keys"
    fi
    read -p "📝 Paste OPENROUTER_API_KEY (press Enter to skip): " USER_OR || true
    if [ -n "$USER_OR" ]; then
        set_env_key "OPENROUTER_API_KEY" "$USER_OR"
        set_env_key "OPENROUTER_MODEL" "meta-llama/llama-3.3-70b-instruct:free"
        read -p "👉 Set OpenRouter as your active LLM provider (LLM_PROVIDER=openrouter)? [y/N]: " SET_OR_ACTIVE || true
        if [[ "$SET_OR_ACTIVE" =~ ^[Yy]$ ]]; then
            set_env_key "LLM_PROVIDER" "openrouter"
            echo "   ✅ Set LLM_PROVIDER=openrouter with free model meta-llama/llama-3.3-70b-instruct:free"
        fi
        echo "   ✅ Saved OPENROUTER_API_KEY to backend/.env"
    fi
    echo ""

    # --------------------------------------------------------------------------
    # 5.4 Razorpay Test Mode Setup & Credentials (With detailed guide)
    # --------------------------------------------------------------------------
    echo "=================================================================="
    echo "💳 [4/4] Razorpay Test Mode Setup Guide"
    echo "=================================================================="
    echo "Follow these steps to obtain free Test Mode credentials:"
    echo "  1. Sign in or create an account at https://dashboard.razorpay.com"
    echo "  2. Ensure the top-right toggle is switched to 'TEST MODE' (never live)."
    echo "  3. Go to: Account & Settings -> API Keys (or direct link below)."
    echo "  4. Click 'Generate Test Key' to copy your Key ID and Key Secret."
    echo "     • Key ID:     Starts with 'rzp_test_...'"
    echo "     • Key Secret: 24-character confidential secret string."
    echo "  5. (Optional) Go to Webhooks to configure your test webhook secret."
    echo "=================================================================="
    read -p "👉 Open Razorpay Test API Keys page in browser? [y/N]: " OPEN_RZP || true
    if [[ "$OPEN_RZP" =~ ^[Yy]$ ]]; then
        echo "🚀 Opening Razorpay Dashboard Keys..."
        open_url "https://dashboard.razorpay.com/#/app/keys"
    fi
    read -p "📝 Paste RAZORPAY_KEY_ID (rzp_test_... or Enter to skip): " USER_RZP_KEY || true
    if [ -n "$USER_RZP_KEY" ]; then
        set_env_key "RAZORPAY_KEY_ID" "$USER_RZP_KEY"
        echo "   ✅ Saved RAZORPAY_KEY_ID to backend/.env"
    fi
    read -p "📝 Paste RAZORPAY_KEY_SECRET (press Enter to skip): " USER_RZP_SEC || true
    if [ -n "$USER_RZP_SEC" ]; then
        set_env_key "RAZORPAY_KEY_SECRET" "$USER_RZP_SEC"
        echo "   ✅ Saved RAZORPAY_KEY_SECRET to backend/.env"
    fi
    read -p "📝 Paste RAZORPAY_WEBHOOK_SECRET (press Enter to skip): " USER_RZP_WH || true
    if [ -n "$USER_RZP_WH" ]; then
        set_env_key "RAZORPAY_WEBHOOK_SECRET" "$USER_RZP_WH"
        echo "   ✅ Saved RAZORPAY_WEBHOOK_SECRET to backend/.env"
    fi
fi

echo ""
echo "=================================================================="
echo "🎉 SETUP COMPLETE! Environment configured successfully."
echo "=================================================================="
echo ""
echo "👉 To start the Full Stack (Backend + Frontend):"
echo "   ./bin/start.sh"
echo ""
echo "👉 To run tests & architecture linter:"
echo "   ./bin/test.sh"
echo ""
echo "👉 To run 4 automated end-to-end demo scenarios:"
echo "   ./bin/run_scenarios.sh"
echo "=================================================================="
