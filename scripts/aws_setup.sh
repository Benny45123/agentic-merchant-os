#!/usr/bin/env bash
set -e

echo "========================================================="
echo "   Agentic Merchant OS - AWS EC2 One-Click Bootstrap    "
echo "========================================================="

# 1. Update system packages
echo "==> Updating apt repositories..."
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg lsb-release git ufw

# 2. Install Docker & Docker Compose
if ! command -v docker &> /dev/null; then
    echo "==> Installing official Docker Engine..."
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo usermod -aG docker $USER
    echo "==> Docker installed successfully!"
else
    echo "==> Docker is already installed."
fi

# 3. Configure Firewall (UFW)
echo "==> Configuring firewall rules (SSH 22, HTTP 80, HTTPS 443, Next 3000, API 8000)..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 3000/tcp
sudo ufw allow 8000/tcp
sudo ufw --force enable

# 4. Clone or update repository
APP_DIR="$HOME/agentic-merchant-os"
if [ ! -d "$APP_DIR" ]; then
    echo "==> Setting up project directory at $APP_DIR..."
    git clone https://github.com/Benny45123/agentic-merchant-os.git "$APP_DIR"
fi

cd "$APP_DIR"

if [ ! -f ".env" ]; then
    echo "==> Creating default .env from .env.example..."
    cp .env.example .env
fi

mkdir -p data

echo "========================================================="
echo "   AWS Bootstrap Complete!                               "
echo "========================================================="
echo "Public IP: $(curl -s http://checkip.amazonaws.com || echo unknown)"
echo ""
echo "Next Steps:"
echo "1. Edit .env with your live keys: nano $APP_DIR/.env"
echo "2. Start stack: docker compose up -d --build"
echo "3. Check logs:  docker compose logs -f"
echo "========================================================="
