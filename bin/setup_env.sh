#!/usr/bin/env bash
# ==============================================================================
# Agentic Merchant OS - Universal Setup Script (Pure UV Package Manager)
# Auto-installs 'uv' if missing + Python 3.12 + Auto JWT Secret + API Setup Wizard
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=================================================================="
echo "🚀 Setting up Agentic Merchant OS (Pure UV Engine)"
echo "📁 Repository Root: $REPO_ROOT"
echo "=================================================================="

# Ensure path includes standard local bin locations for uv
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:/usr/local/bin:$PATH"

# ------------------------------------------------------------------------------
# STEP 1: Auto-Install 'uv' if not present
# ------------------------------------------------------------------------------
if ! command -v uv >/dev/null 2>&1; then
    echo ""
    echo "⚡ 'uv' package manager not found on system."
    echo "📦 Auto-installing standalone Astral 'uv' binary..."
    if command -v curl >/dev/null 2>&1; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
    elif command -v wget >/dev/null 2>&1; then
        wget -qO- https://astral.sh/uv/install.sh | sh
    else
        echo "❌ Error: Neither curl nor wget was found. Please install 'uv' from https://docs.astral.sh/uv/"
        exit 1
    fi

    # Re-export PATH with newly installed uv location
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    if [ -f "$HOME/.cargo/env" ]; then
        source "$HOME/.cargo/env"
    fi
fi

if command -v uv >/dev/null 2>&1; then
    echo "✅ Using 'uv' version: $(uv --version)"
else
    echo "❌ Error: Failed to initialize 'uv'. Please check your PATH or install manually from https://astral.sh/uv"
    exit 1
fi

cd "$REPO_ROOT/backend"

# Ensure backend .env exists
if [ ! -f ".env" ]; then
    echo "📄 Creating backend/.env from .env.example..."
    cp "$REPO_ROOT/.env.example" "$REPO_ROOT/backend/.env"
fi

# ------------------------------------------------------------------------------
# STEP 2: Auto-Generate Secure JWT Signing Key (if placeholder or empty)
# ------------------------------------------------------------------------------
CURRENT_JWT_KEY=$(grep "^JWT_SIGNING_KEY=" .env | cut -d '=' -f2- || true)
if [ -z "$CURRENT_JWT_KEY" ] || [[ "$CURRENT_JWT_KEY" == *"change_this"* ]] || [[ "$CURRENT_JWT_KEY" == *"your_jwt"* ]] || [ ${#CURRENT_JWT_KEY} -lt 32 ]; then
    echo "🔑 Generating secure random 64-character JWT Signing Key..."
    if command -v openssl >/dev/null 2>&1; then
        RAND_KEY=$(openssl rand -hex 32)
    else
        RAND_KEY=$(uv run python -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || date +%s%N | sha256sum | head -c 64)
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
# STEP 3: Setup Isolated Python 3.12 Virtual Environment using UV
# ------------------------------------------------------------------------------
echo ""
echo "🐍 [1/4] Configuring Python 3.12 environment via uv..."

# Ensure Python 3.12 is fetched by uv automatically if not present
echo "📦 Ensuring Python 3.12 toolchain via uv..."
uv python install 3.12 || true

# Create .venv if not already present
if [ ! -d ".venv" ]; then
    echo "🔨 Creating new .venv with Python 3.12..."
    uv venv .venv --python 3.12
else
    echo "✅ Existing .venv detected, reusing environment..."
fi

# Activate virtualenv
source .venv/bin/activate

# Install backend dependencies via uv pip
echo "⚡ Installing backend dependencies via uv pip..."
uv pip install -r requirements.txt
echo "✅ Backend dependencies successfully installed!"

# ------------------------------------------------------------------------------
# STEP 4: Run Database Migrations & Idempotent Seed
# ------------------------------------------------------------------------------
echo ""
echo "🗄️ [2/4] Running database migrations and idempotent seed..."
alembic upgrade head
python -m app.seed
echo "✅ Database initialized and seeded with products, merchant, and policies."

# ------------------------------------------------------------------------------
# STEP 5: Setup Frontend Dependencies
# ------------------------------------------------------------------------------
echo ""
echo "💻 [3/4] Setting up frontend dependencies..."
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
# STEP 6: Step-by-Step API Provider Setup & Credentials Assistant
# ------------------------------------------------------------------------------
echo ""
echo "=================================================================="
echo "🌐 [4/4] Step-by-Step API Provider Setup Wizard"
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
    # 6.1 Google Gemini API Key
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
    # 6.2 Groq Cloud API Key
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
    # 6.3 OpenRouter API Key
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
    # 6.4 Razorpay Test Mode Setup & Credentials
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
        if [ -f "$REPO_ROOT/frontend/.env.local" ]; then
            if grep -q "^NEXT_PUBLIC_RAZORPAY_KEY_ID=" "$REPO_ROOT/frontend/.env.local"; then
                sed -i.bak "s|^NEXT_PUBLIC_RAZORPAY_KEY_ID=.*|NEXT_PUBLIC_RAZORPAY_KEY_ID=$USER_RZP_KEY|" "$REPO_ROOT/frontend/.env.local" && rm -f "$REPO_ROOT/frontend/.env.local.bak"
            else
                echo "NEXT_PUBLIC_RAZORPAY_KEY_ID=$USER_RZP_KEY" >> "$REPO_ROOT/frontend/.env.local"
            fi
            echo "   ✅ Synced NEXT_PUBLIC_RAZORPAY_KEY_ID to frontend/.env.local"
        fi
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
    echo ""

    # --------------------------------------------------------------------------
    # 6.5 Telegram Bot Mobile Gateway Setup
    # --------------------------------------------------------------------------
    echo "=================================================================="
    echo "🤖 [5/5] Telegram Bot Mobile Gateway (@agentic_merchant_store_bot)"
    echo "=================================================================="
    echo "Enable real mobile shopping & A2A wholesale bargaining on your phone."
    echo "  1. Open Telegram and search for @BotFather (or open link below)."
    echo "  2. Send /newbot, give it a name and username ending in 'bot'."
    echo "  3. Copy the HTTP API token."
    echo "=================================================================="
    read -p "👉 Open Telegram @BotFather in browser/app? [y/N]: " OPEN_TG || true
    if [[ "$OPEN_TG" =~ ^[Yy]$ ]]; then
        echo "🚀 Opening @BotFather..."
        open_url "https://t.me/BotFather"
    fi
    read -p "📝 Paste TELEGRAM_BOT_TOKEN (or press Enter to keep default): " USER_TG_TOKEN || true
    if [ -n "$USER_TG_TOKEN" ]; then
        set_env_key "TELEGRAM_BOT_TOKEN" "$USER_TG_TOKEN"
        echo "   ✅ Saved TELEGRAM_BOT_TOKEN to backend/.env"
    fi
fi


echo ""
echo "=================================================================="
echo "🎉 SETUP COMPLETE! Environment configured with pure 'uv' speed."
echo "=================================================================="
echo ""
echo "👉 To start the Full Stack (Backend + Frontend):"
echo "   ./bin/start.sh"
echo ""
echo "👉 To run tests & architecture linter:"
echo "   ./bin/test.sh"
echo ""
echo "👉 To run 6 automated end-to-end demo scenarios:"
echo "   ./bin/run_scenarios.sh"
echo "=================================================================="
