import os
import sys
from pathlib import Path
import pytest

# Ensure repository root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.check_import_graph import check_import_boundaries, Violation


def test_import_graph_lint_clean_skeleton():
    """Asserts that the current repository skeleton passes the import boundary check with 0 violations."""
    app_dir = REPO_ROOT / "backend" / "app"
    violations = check_import_boundaries(app_dir)
    assert len(violations) == 0, f"Expected 0 violations on clean skeleton, found: {violations}"


def test_import_graph_flags_commerce_agent_calling_razorpay(tmp_path: Path):
    """Rule 1: FAIL if app/commerce_agent imports app/razorpay_adapter."""
    mock_app_dir = tmp_path / "app"
    commerce_agent_dir = mock_app_dir / "commerce_agent"
    commerce_agent_dir.mkdir(parents=True)
    
    violation_file = commerce_agent_dir / "bad_agent.py"
    violation_file.write_text("from app.razorpay_adapter import RazorpayAdapter\n", encoding="utf-8")
    
    violations = check_import_boundaries(mock_app_dir)
    assert len(violations) == 1
    assert "Rule 1" in violations[0].rule
    assert violations[0].import_statement == "app.razorpay_adapter"


def test_import_graph_flags_guardian_calling_ai_provider(tmp_path: Path):
    """Rule 3: FAIL if app/guardian imports app/ai_provider."""
    mock_app_dir = tmp_path / "app"
    guardian_dir = mock_app_dir / "guardian"
    guardian_dir.mkdir(parents=True)
    
    violation_file = guardian_dir / "bad_guardian.py"
    violation_file.write_text("import app.ai_provider\n", encoding="utf-8")
    
    violations = check_import_boundaries(mock_app_dir)
    assert len(violations) == 1
    assert "Rule 3" in violations[0].rule
    assert violations[0].import_statement == "app.ai_provider"


def test_import_graph_flags_mandate_importing_api(tmp_path: Path):
    """Rule 4: FAIL if app/mandate imports app/api."""
    mock_app_dir = tmp_path / "app"
    mandate_dir = mock_app_dir / "mandate"
    mandate_dir.mkdir(parents=True)
    
    violation_file = mandate_dir / "bad_mandate.py"
    violation_file.write_text("from app.api import router\n", encoding="utf-8")
    
    violations = check_import_boundaries(mock_app_dir)
    assert len(violations) == 1
    assert "Rule 4" in violations[0].rule
