# 🚀 Agentic Merchant OS — Complete AWS Deployment & CI/CD Guide

This guide provides the complete, production-grade roadmap to deploy **Agentic Merchant OS (AMOS)** to **Amazon Web Services (AWS)** using **Docker Compose** and automated **GitHub Actions CI/CD**.

---

## 🏛️ Deployment Architecture Overview

```
                          [ Internet / Shoppers / AI Buyers ]
                                           │
                                           ▼ (Ports 80 / 443 / 3000 / 8000)
             ┌───────────────────────────────────────────────────────────┐
             │                   AWS EC2 (Ubuntu 24.04)                  │
             │                                                           │
             │   ┌─────────────────────┐       ┌─────────────────────┐   │
             │   │ Next.js 14 Frontend │ ◄────►│   FastAPI Backend   │   │
             │   │    (Port 3000)      │       │     (Port 8000)     │   │
             │   └─────────────────────┘       └──────────┬──────────┘   │
             │                                            │              │
             │   ┌─────────────────────┐                  │              │
             │   │ Telegram Bot Daemon │ ◄────────────────┘              │
             │   │   (@agentic_bot)    │                  ▼              │
             │   └─────────────────────┘       ┌─────────────────────┐   │
             │                                 │   SQLite WAL Mode   │   │
             │                                 │   (NVMe EBS Volume) │   │
             │                                 └─────────────────────┘   │
             └───────────────────────────────────────────────────────────┘
```

* **Zero-RDS Overhead**: SQLite in Write-Ahead Logging (WAL) mode runs directly against fast local NVMe/EBS storage (`/app/data/amos.db`), delivering sub-15ms query times with zero multi-database networking latency or recurring RDS expenses.
* **Persistent Storage**: All transaction receipts, Google AP2 mandate chains, and orders survive container redeployments via mounted Docker volumes (`./data:/app/data`).

---

## 📋 Phase 1: Launch Your AWS EC2 Instance

1. **Log in to the [AWS Management Console](https://console.aws.amazon.com/)** and navigate to **EC2**.
2. Click **Launch Instance** with the following settings:
   - **Name**: `agentic-merchant-os-prod`
   - **OS Image (AMI)**: **Ubuntu Server 24.04 LTS** (or 22.04 LTS), 64-bit (x86_64).
   - **Instance Type**: `t3.small` (2 vCPU, 2 GB RAM) or `t3.medium` (2 vCPU, 4 GB RAM recommended for fast builds).
   - **Key Pair**: Create or select an existing key pair (`.pem`), e.g., `amos-aws-key.pem`.
3. **Network & Security Group Inbound Rules**:
   - `Port 22 (SSH)` ➔ `Anywhere (0.0.0.0/0)` or `My IP`
   - `Port 80 (HTTP)` ➔ `Anywhere (0.0.0.0/0)`
   - `Port 443 (HTTPS)` ➔ `Anywhere (0.0.0.0/0)`
   - `Port 3000 (Custom TCP - Frontend)` ➔ `Anywhere (0.0.0.0/0)`
   - `Port 8000 (Custom TCP - Backend)` ➔ `Anywhere (0.0.0.0/0)`
4. **Storage**: Configure **20 GB gp3 SSD** root volume.
5. Click **Launch Instance**.
6. *(Recommended)* Under **Network & Security ➔ Elastic IPs**, allocate an Elastic IP and associate it with your EC2 instance so the public IP never changes on reboot.

---

## ⚡ Phase 2: One-Click Instance Bootstrap

1. Connect to your instance via SSH from your terminal:
   ```bash
   chmod 400 amos-aws-key.pem
   ssh -i amos-aws-key.pem ubuntu@<YOUR_EC2_PUBLIC_IP>
   ```

2. Run the automated AMOS bootstrap script:
   ```bash
   curl -sSL https://raw.githubusercontent.com/Benny45123/agentic-merchant-os/main/scripts/aws_setup.sh | bash
   ```
   *This script automatically updates Ubuntu, installs Docker & Docker Compose plugin, configures the UFW firewall, clones the repo, and creates the persistent `./data` directory.*

3. Log out and log back in to apply Docker group permissions:
   ```bash
   exit
   ssh -i amos-aws-key.pem ubuntu@<YOUR_EC2_PUBLIC_IP>
   ```

4. Configure your production environment variables:
   ```bash
   cd ~/agentic-merchant-os
   nano .env
   ```
   *Update the following variables with your actual keys:*
   ```ini
   RAZORPAY_KEY_ID=rzp_test_...
   RAZORPAY_KEY_SECRET=...
   RAZORPAY_WEBHOOK_SECRET=...
   GEMINI_API_KEY=...
   JWT_SIGNING_KEY=generate_a_random_32_char_key
   TELEGRAM_BOT_TOKEN=...
   NEXT_PUBLIC_API_BASE_URL=http://<YOUR_EC2_PUBLIC_IP>:8000
   MERCHANT_API_BASE=http://backend:8000
   BACKEND_PUBLIC_URL=http://<YOUR_EC2_PUBLIC_IP>:8000
   ```

5. Build and launch the stack:
   ```bash
   docker compose up -d --build
   ```

6. Verify that all 3 services are online:
   ```bash
   docker compose ps
   curl http://localhost:8000/health
   ```
   *Expected response: `{"status":"ok","timestamp":"..."}`*

---

## 🔄 Phase 3: Automated CI/CD with GitHub Actions

The repository includes two pre-configured GitHub Actions workflows in `.github/workflows/`:
* **`ci.yml`**: Runs on every Pull Request and Push. Executes all **57 Pytests**, the **Architecture Import-Graph Linter**, and tests the **Next.js Production Build**.
* **`deploy.yml`**: Deploys automatically to AWS on push to `main` or via manual 1-click trigger.

### Configuring GitHub Secrets:

In your GitHub repository, go to **Settings ➔ Secrets and variables ➔ Actions** and add the following **Repository Secrets**:

| Secret Name | Value | Description |
| :--- | :--- | :--- |
| `AWS_EC2_HOST` | `<YOUR_EC2_PUBLIC_IP>` | Your EC2 Elastic IP or Public IPv4 address. |
| `AWS_EC2_USER` | `ubuntu` | The default SSH username for Ubuntu instances. |
| `AWS_SSH_PRIVATE_KEY` | `-----BEGIN OPENSSH PRIVATE KEY-----...` | Paste the **entire content** of your `amos-aws-key.pem` file. |
| `AWS_SSH_PORT` | `22` | *(Optional, defaults to 22)* |

### How Continuous Deployment Works:
Whenever you push new code to `main`:
1. GitHub Actions runs the complete test suite.
2. If tests pass, GitHub Actions connects via SSH to your AWS EC2 instance.
3. It runs `git fetch origin main && git reset --hard origin/main`.
4. It rebuilds the Docker images and restarts containers with zero manual effort.
5. It runs a live health check on `http://localhost:8000/health`.

---

## 🌐 Phase 4: Custom Domain & Free Let's Encrypt SSL (Caddy)

If you have a domain (e.g. `amos.yourdomain.com`):
1. Add an **A Record** in your DNS provider pointing `amos.yourdomain.com` to your EC2 Elastic IP.
2. In your `~/agentic-merchant-os/.env` file on EC2, set:
   ```ini
   DOMAIN=amos.yourdomain.com
   ```
3. Run Caddy reverse proxy:
   ```bash
   docker compose up -d caddy
   ```
   *Caddy will automatically request and renew a free Let's Encrypt SSL certificate!*

---

## 📱 Phase 5: Live Telegram Mobile Bot Verification

The Telegram bot runs as a native background daemon inside the `amos-telegram-bot` container.
1. In your Telegram app, search for your bot username (`@agentic_merchant_store_bot`).
2. Send `/start`.
3. The bot communicates directly with the live AWS backend, allowing judges and shoppers to browse products and negotiate deals in real time from anywhere in the world.

---

## 🛠️ Maintenance & Useful Commands

| Task | Command on EC2 |
| :--- | :--- |
| **Stream Live Logs** | `docker compose logs -f` |
| **Stream Backend Logs Only** | `docker compose logs -f backend` |
| **Restart Stack** | `docker compose restart` |
| **Rebuild Containers** | `docker compose up -d --build` |
| **Inspect Running Containers** | `docker compose ps` |
| **Run Pytest Inside Container** | `docker compose exec backend pytest backend/tests` |
| **Backup Database** | `cp data/amos.db data/amos_backup_$(date +%Y%m%d).db` |
