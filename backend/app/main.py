from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dashboard import router as dashboard_router
from app.api.uap_gateway import router as uap_router
from app.campaign.router import router as campaign_router
from app.catalog.router import router as catalog_router
from app.commerce_agent.router import router as agent_router
from app.guardian.router import router as guardian_router
from app.mandate.router import router as mandate_router
from app.negotiation.router import router as negotiation_router
from app.policy.router import router as policy_router
from app.razorpay_adapter.router import router as razorpay_router
from app.receipts.router import router as receipts_router

app = FastAPI(
    title="Agentic Merchant OS API",
    description="Deterministic Guardian and AI Agentic Commerce Backend (Razorpay Buildathon Track 01)",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
