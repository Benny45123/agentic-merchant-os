# 🚀 Clean Native PM2 Deployment Plan (Single AWS EC2 Instance)

This is the exact, zero-overhead, step-by-step guide to deploying **Agentic Merchant OS** using native runtimes (Python 3.12, Node.js 20), **PM2 Process Manager**, and **Permanent Free HTTPS (`sslip.io` + Caddy)** on a single AWS EC2 instance.

* Total Setup Time: **~5 to 7 minutes**
* Total 3-Day Cost: **~$1.50 to $2.00 (~₹145 INR)**
* Runtime RAM: **~450 MB (Leaves >1.5 GB Free on `t3.small`)**
* HTTPS Domain: **Permanent, free forever, never changes on reboot!**

---

## 📋 Step 0: Launch AWS EC2 Instance & Lock Elastic IP

1. **Go to AWS EC2 Console ➔ Launch Instance**:
   - **Name**: `agentic-merchant-os`
   - **AMI**: **Ubuntu Server 24.04 LTS** (64-bit x86)
   - **Instance Type**: **`t3.small`** (2 vCPU, 2 GB RAM) *(or `t3.micro` if on AWS Free Tier)*
   - **Key Pair**: Create or select `amos-key.pem`
   - **Storage**: **20 GB gp3 SSD**
2. **Security Group Inbound Rules**:
   - `Port 22 (SSH)` ➔ Source: **`My IP`** *(Protects against unauthorized SSH attempts)*
   - `Port 80 (HTTP)` ➔ Source: **`Anywhere (0.0.0.0/0)`**
   - `Port 443 (HTTPS)` ➔ Source: **`Anywhere (0.0.0.0/0)`**
   - `Port 3000 (Next.js UI)` ➔ Source: **`Anywhere (0.0.0.0/0)`**
   - `Port 8000 (FastAPI API)` ➔ Source: **`Anywhere (0.0.0.0/0)`**
3. Click **Launch Instance**.
4. **🔒 Lock Your Elastic IP (Crucial so IP never changes)**:
   - In the left sidebar, click **Elastic IPs** ➔ **Allocate Elastic IP address** ➔ **Allocate**.
   - Select the newly allocated Elastic IP ➔ **Actions ➔ Associate Elastic IP address**.
   - Select your running instance `agentic-merchant-os` and click **Associate**.
   - Note your permanent IP (e.g. `3.110.42.18`).

---

## 💻 Step 1: Connect via SSH

From your local computer terminal:

```bash
chmod 400 amos-key.pem
ssh -i amos-key.pem ubuntu@<YOUR_EC2_PUBLIC_IP>
```

---

## 🛡️ Step 2: 10-Second Anti-OOM Shield (4GB Swap Space)

Run this copy-paste block on EC2. It creates a 4GB virtual memory file on the NVMe SSD so that Next.js compilation will **NEVER crash with Out Of Memory (OOM)**:

```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 📦 Step 3: Install Node.js 20, Python 3.12, PM2 & Caddy (60 Seconds)

Run this single block on EC2 to install all runtimes and Caddy:

```bash
# 1. Update and install basic tools
sudo apt update && sudo apt install -y python3-pip python3-venv git curl debian-keyring debian-archive-keyring apt-transport-https

# 2. Install Node.js 20 & PM2
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2

# 3. Install Caddy (for permanent free auto-HTTPS)
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install -y caddy
```

---

## 📂 Step 4: Clone Repository & Configure `.env` (60 Seconds)

```bash
git clone https://github.com/Benny45123/agentic-merchant-os.git
cd agentic-merchant-os
cp .env.example .env
nano .env
```

### In `.env`, configure your permanent domain:
*Replace `3-110-42-18` with your actual Elastic IP with dashes instead of dots!*

```ini
# Database
DATABASE_URL=sqlite+aiosqlite:///./amos.db

# Permanent Free HTTPS URLs (Replace 3-110-42-18 with your Elastic IP!)
BACKEND_PUBLIC_URL=https://3-110-42-18.sslip.io
NEXT_PUBLIC_API_BASE_URL=https://3-110-42-18.sslip.io
MERCHANT_API_BASE=http://localhost:8000

# Razorpay Test Mode Credentials
RAZORPAY_KEY_ID=rzp_test_...
RAZORPAY_KEY_SECRET=...
RAZORPAY_WEBHOOK_SECRET=...

# AI Model Keys
LLM_PROVIDER=gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-3.5-flash-lite

# Security Secret
JWT_SIGNING_KEY=d7b5f92a4e1c8b3f6a9e2d5c8b1a4f7e

# Telegram Mobile Gateway
TELEGRAM_BOT_TOKEN=...

ENV=production
```
*(Press `Ctrl+O` then `Enter` to save, and `Ctrl+X` to exit nano)*.

---

## ⚡ Step 5: Run Universal Setup (90 Seconds)

Run the platform setup script:

```bash
./bin/setup_env
```

*This automatically creates the Python 3.12 virtualenv in `backend/.venv`, runs Alembic migrations (including Google AP2 mandate tables), loads initial seed products/policies, and builds Next.js (`npm run build`).*

---

## 🚀 Step 6: Launch Everything with PM2 (10 Seconds)

Start Backend, Frontend, and Telegram Bot as managed background services:

```bash
# 1. Start FastAPI Backend (Port 8000)
pm2 start "backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000" --name "backend" --cwd backend

# 2. Start Next.js Frontend (Port 3000)
pm2 start "npm run start" --name "frontend" --cwd frontend

# 3. Start Telegram Bot Daemon (Long-polling)
pm2 start "backend/.venv/bin/python -m app.telegram.bot" --name "telegram-bot" --cwd backend

# 4. Make PM2 restart automatically if the server reboots:
pm2 save
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u ubuntu --hp /home/ubuntu
```

---

## 🔒 Step 7: Activate Permanent Free HTTPS via Caddy (30 Seconds)

Configure Caddy to give you real Let's Encrypt HTTPS certificates for your permanent domain:

*(Replace `3-110-42-18.sslip.io` with your actual Elastic IP with dashes!)*

```bash
sudo bash -c 'cat << "EOF" > /etc/caddy/Caddyfile
3-110-42-18.sslip.io {
    # Backend API endpoints
    handle /catalog* {
        reverse_proxy localhost:8000
    }
    handle /commerce* {
        reverse_proxy localhost:8000
    }
    handle /mandates* {
        reverse_proxy localhost:8000
    }
    handle /receipts* {
        reverse_proxy localhost:8000
    }
    handle /policy* {
        reverse_proxy localhost:8000
    }
    handle /campaigns* {
        reverse_proxy localhost:8000
    }
    handle /payments* {
        reverse_proxy localhost:8000
    }
    handle /dashboard/api* {
        reverse_proxy localhost:8000
    }
    handle /health {
        reverse_proxy localhost:8000
    }
    handle /.well-known* {
        reverse_proxy localhost:8000
    }
    handle /docs* {
        reverse_proxy localhost:8000
    }
    handle /openapi.json {
        reverse_proxy localhost:8000
    }

    # Everything else goes to Next.js Frontend
    handle {
        reverse_proxy localhost:3000
    }
}
EOF'

# Restart Caddy to acquire real Let's Encrypt SSL:
sudo systemctl restart caddy
```

---

## ✅ Step 8: Verify Everything is Live!

Check PM2 status:
```bash
pm2 status
```

### 🌐 Live Permanent URLs (Ready for Demo & Pitch Video):
* **Store & Buyer Chat (with Voice Mic)**: `https://<YOUR-IP>.sslip.io`
* **A2A Negotiation Arena**: `https://<YOUR-IP>.sslip.io/negotiate`
* **Merchant Financial Dashboard**: `https://<YOUR-IP>.sslip.io/dashboard`
* **Decision Receipts & Merkle Trees**: `https://<YOUR-IP>.sslip.io/receipts`
* **API Swagger Docs**: `https://<YOUR-IP>.sslip.io/docs`
* **Telegram Bot Mobile Gateway**: `@agentic_merchant_store_bot` (Test payments open over HTTPS with 0 mobile warnings!)

---

## 🛠️ Handy Day-to-Day PM2 Commands

| Task | Command on EC2 |
| :--- | :--- |
| **View Live Real-Time Logs** | `pm2 logs` |
| **View Backend Logs Only** | `pm2 logs backend` |
| **View Telegram Logs Only** | `pm2 logs telegram-bot` |
| **Check RAM & CPU Usage** | `pm2 monit` |
| **Restart Everything After a Code Edit** | `git pull && pm2 restart all` |
| **Stop All (e.g. at night to save cost)** | `pm2 stop all` |
| **Start All Back Up** | `pm2 start all` |
