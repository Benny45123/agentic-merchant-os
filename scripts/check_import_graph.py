#!/usr/bin/env python3
"""
Architecture Import-Graph Linter
Enforces non-negotiable architectural boundaries defined in docs/02_SYSTEM_ARCHITECTURE.md §4
and docs/14_TEST_PLAN.md §3:

1. FAIL if: app/commerce_agent imports app/razorpay_adapter
2. FAIL if: app/campaign imports app/razorpay_adapter
3. FAIL if: app/guardian imports app/ai_provider
4. FAIL if: app/mandate or app/policy import anything from app/api, app/commerce_agent, app/campaign, app/ai_provider
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, NamedTuple


class Violation(NamedTuple):
    file_path: Path
    line_number: int
    rule: str
    import_statement: str


def get_imports_from_file(file_path: Path) -> List[tuple[int, str]]:
    """Parse python file and return list of (lineno, imported_module_string)."""
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(file_path))
        except SyntaxError as e:
            print(f"Syntax error parsing {file_path}: {e}", file=sys.stderr)
            return []

    imports: List[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append((node.lineno, node.module))
    return imports


def check_import_boundaries(app_dir: Path) -> List[Violation]:
    violations: List[Violation] = []

    for root, _, files in os.walk(app_dir):
        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = Path(root) / file
            rel_path = file_path.relative_to(app_dir.parent).as_posix()
            
            imports = get_imports_from_file(file_path)

            for lineno, imp in imports:
                # Rule 1: app/commerce_agent never imports app/razorpay_adapter
                if "app/commerce_agent" in rel_path:
                    if imp.startswith("app.razorpay_adapter") or imp == "razorpay_adapter":
                        violations.append(Violation(
                            file_path=file_path,
                            line_number=lineno,
                            rule="Rule 1: app/commerce_agent must NOT import app/razorpay_adapter",
                            import_statement=imp
                        ))

                # Rule 2: app/campaign never imports app/razorpay_adapter
                if "app/campaign" in rel_path:
                    if imp.startswith("app.razorpay_adapter") or imp == "razorpay_adapter":
                        violations.append(Violation(
                            file_path=file_path,
                            line_number=lineno,
                            rule="Rule 2: app/campaign must NOT import app/razorpay_adapter",
                            import_statement=imp
                        ))

                # Rule 3: app/guardian never imports app/ai_provider
                if "app/guardian" in rel_path:
                    if imp.startswith("app.ai_provider") or imp == "ai_provider":
                        violations.append(Violation(
                            file_path=file_path,
                            line_number=lineno,
                            rule="Rule 3: app/guardian must NOT import app/ai_provider (Guardian must be deterministic)",
                            import_statement=imp
                        ))

                # Rule 4: app/mandate or app/policy must NOT import from app/api, app/commerce_agent, app/campaign, app/ai_provider
                if "app/mandate" in rel_path or "app/policy" in rel_path:
                    forbidden_targets = [
                        "app.api", "api",
                        "app.commerce_agent", "commerce_agent",
                        "app.campaign", "campaign",
                        "app.ai_provider", "ai_provider"
                    ]
                    for target in forbidden_targets:
                        if imp == target or imp.startswith(target + "."):
                            violations.append(Violation(
                                file_path=file_path,
                                line_number=lineno,
                                rule=f"Rule 4: app/mandate and app/policy must NOT import from {target}",
                                import_statement=imp
                            ))

    return violations


def main() -> int:
    # Locate backend/app directory
    repo_root = Path(__file__).resolve().parent.parent
    app_dir = repo_root / "backend" / "app"
    if not app_dir.exists():
        # Maybe invoked from inside backend/
        app_dir = repo_root / "app"

    if not app_dir.exists():
        print(f"Error: app directory not found at {app_dir}", file=sys.stderr)
        return 2

    print(f"Checking architecture import graph for: {app_dir}")
    violations = check_import_boundaries(app_dir)

    if violations:
        print(f"\n❌ [ARCHITECTURE VIOLATION] Found {len(violations)} forbidden import(s):\n")
        for v in violations:
            print(f"  • {v.file_path}:{v.line_number} -> '{v.import_statement}'")
            print(f"    Violation: {v.rule}\n")
        return 1
    else:
        print("\n✅ [OK] Import-graph boundary check passed cleanly! All architectural rules satisfied.\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
