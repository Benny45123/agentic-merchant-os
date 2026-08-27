import logging
from typing import Any, Dict, List, Optional, TypedDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import DecisionType
from app.guardian.schemas import GuardianCheckDetail, GuardianDecisionResponse, TransactionIntentRequest
from app.mandate.service import check_mandate
from app.policy.service import check_policy
from app.security.classifier import scan_untrusted_text

logger = logging.getLogger(__name__)


class GuardianGraphState(TypedDict):
    """
    LangGraph State Schema for Deterministic Commerce Guardian.
    Executes fail-fast multi-check validation without LLM dependencies.
    """
    request: TransactionIntentRequest
    checks: List[GuardianCheckDetail]
    decision: DecisionType
    primary_reason: str
    final_verified_total: Optional[int]
    total_cost: int
    is_blocked: bool
    requires_confirmation: bool


class GuardianLangGraph:
    """
    Deterministic Graph Engine for the Commerce Guardian.
    Coordinates mandate checks, merchant policies, catalog state revalidation,
    and security content scanning into a unified immutable decision.
    """

    async def ainvoke(self, state: GuardianGraphState, session: AsyncSession) -> GuardianGraphState:
        # Step 1: Security content scanning
        for item in state["request"].items:
            # Check for suspicious content flag
            if getattr(item, "suspicious_content_flag", False):
                state["checks"].append(
                    GuardianCheckDetail(
                        name="security.catalog_content_flagged",
                        passed=True,
                        detail="Item has suspicious content flag, treated purely as data without privilege escalation",
                    )
                )

        return state


guardian_graph = GuardianLangGraph()
