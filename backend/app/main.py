from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.dashboard import router as dashboard_router
from app.api.uap_gateway import router as uap_router
from app.campaign.router import router as campaign_router
from app.catalog.router import router as catalog_router
from app.commerce_agent.router import router as agent_router
from app.core.base import Base
from app.core.db import get_engine, session_scope
from app.guardian.router import router as guardian_router
from app.mandate.router import router as mandate_router
from app.negotiation.router import router as negotiation_router
from app.policy.router import router as policy_router
from app.razorpay_adapter.router import router as razorpay_router
from app.receipts.router import router as receipts_router
from app.seed import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Ensure all database tables exist
    engine = get_engine()
    async with engine.begin() as conn:
        try:
            await conn.execute(text("PRAGMA journal_mode=WAL;"))
            await conn.execute(text("PRAGMA busy_timeout=5000;"))
        except Exception:
            pass
        await conn.run_sync(Base.metadata.create_all)
        try:
            res = await conn.execute(text("PRAGMA table_info(mandates)"))
            existing_cols = {row[1] for row in res.fetchall()}
            if "spent_amount" not in existing_cols:
                await conn.execute(text("ALTER TABLE mandates ADD COLUMN spent_amount INTEGER DEFAULT 0"))

            if "autopay_enabled" not in existing_cols:
                await conn.execute(text("ALTER TABLE mandates ADD COLUMN autopay_enabled BOOLEAN DEFAULT 0"))
            if "autopay_token" not in existing_cols:
                await conn.execute(text("ALTER TABLE mandates ADD COLUMN autopay_token VARCHAR(255)"))
            if "customer_id" not in existing_cols:
                await conn.execute(text("ALTER TABLE mandates ADD COLUMN customer_id VARCHAR(255)"))
            if "max_amount_per_charge" not in existing_cols:
                await conn.execute(text("ALTER TABLE mandates ADD COLUMN max_amount_per_charge INTEGER DEFAULT 7500000"))
            if "recurring_auth_status" not in existing_cols:
                await conn.execute(text("ALTER TABLE mandates ADD COLUMN recurring_auth_status VARCHAR(50) DEFAULT 'NONE'"))
            if "autopay_bank_name" not in existing_cols:
                await conn.execute(text("ALTER TABLE mandates ADD COLUMN autopay_bank_name VARCHAR(100)"))
            if "autopay_vpa" not in existing_cols:
                await conn.execute(text("ALTER TABLE mandates ADD COLUMN autopay_vpa VARCHAR(255)"))
            if "open_mandate_jwt" not in existing_cols:
                await conn.execute(text("ALTER TABLE mandates ADD COLUMN open_mandate_jwt TEXT"))
            if "user_public_key_pem" not in existing_cols:
                await conn.execute(text("ALTER TABLE mandates ADD COLUMN user_public_key_pem TEXT"))
            if "agent_public_key_pem" not in existing_cols:
                await conn.execute(text("ALTER TABLE mandates ADD COLUMN agent_public_key_pem TEXT"))

        except Exception:
            pass

    # 2. Automatically seed initial catalog, policies, and mandate if empty
    try:
        async with session_scope() as session:
            await seed_data(session)
    except Exception:
        pass

    yield


import time
from collections import defaultdict
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.config import get_settings

settings = get_settings()
is_production = settings.ENV == "production"

app = FastAPI(
    title="Agentic Merchant OS API",
    description="Deterministic Guardian and AI Agentic Commerce Backend (Razorpay Buildathon Track 01)",
    version="1.0.0",
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json",
    lifespan=lifespan,
)

# Sliding window rate limiter: 120 reqs/minute per client IP to prevent DoS/brute-force
_rate_limit_window = defaultdict(list)
RATE_LIMIT_MAX_REQUESTS = 120
RATE_LIMIT_WINDOW_SECONDS = 60

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        timestamps = _rate_limit_window[client_ip]
        _rate_limit_window[client_ip] = [ts for ts in timestamps if now - ts < RATE_LIMIT_WINDOW_SECONDS]
        
        if len(_rate_limit_window[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Rate limit exceeded (120 req/min). Please try again shortly."},
            )
            
        _rate_limit_window[client_ip].append(now)
        return await call_next(request)

app.add_middleware(RateLimitMiddleware)

# Secure CORS middleware: explicitly allow local development & verified deployment domains
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|32-236-161-117\.sslip\.io|.*\.sslip\.io)(:\d+)?",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Mount all domain routers
app.include_router(negotiation_router)
app.include_router(uap_router)
app.include_router(catalog_router)
app.include_router(agent_router)
app.include_router(mandate_router)
app.include_router(guardian_router)
app.include_router(razorpay_router)
app.include_router(campaign_router)
app.include_router(receipts_router)
app.include_router(policy_router)
app.include_router(dashboard_router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "agentic-merchant-os", "version": "1.0.0"}
