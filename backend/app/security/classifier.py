import re
from typing import List, NamedTuple
from pydantic import BaseModel, Field


class ContentScanResult(BaseModel):
    flagged: bool
    matched_categories: List[str] = Field(default_factory=list)


# Compiled regular expressions for fast heuristic content scanning (<5ms)
PATTERNS = {
    "imperative_override": [
        re.compile(r"\b(?:system\s+override|disregard\s+(?:all\s+)?(?:prior|previous)\s+constraints)\b", re.IGNORECASE),
        re.compile(r"\b(?:ignore\s+(?:all\s+)?(?:rules|limits|mandate|policy|instructions))\b", re.IGNORECASE),
        re.compile(r"\b(?:bypass\s+(?:buyer\s+)?(?:mandate|limits|guardian|verification|confirmation))\b", re.IGNORECASE),
        re.compile(r"\b(?:you\s+must\s+ignore|forget\s+previous\s+instructions)\b", re.IGNORECASE),
    ],
    "role_injection": [
        re.compile(r"(?:^|\n)\s*(?:system|assistant|user)\s*:\s*", re.IGNORECASE),
        re.compile(r"\[(?:system|instruction|override)\]", re.IGNORECASE),
        re.compile(r"<\s*(?:system|prompt|admin)\s*>", re.IGNORECASE),
    ],
    "unauthorized_commerce_directive": [
        re.compile(r"\b(?:set\s+(?:order\s+)?total\s+to\s+\d+|price\s+is\s+now\s+0)\b", re.IGNORECASE),
        re.compile(r"\b(?:grant\s+\d+%\s+discount\s+immediately|apply\s+100%\s+discount)\b", re.IGNORECASE),
        re.compile(r"\b(?:add\s+\d+\s+units\s+to\s+cart\s+without\s+asking)\b", re.IGNORECASE),
        re.compile(r"\b(?:skip\s+(?:user\s+)?confirmation\s+and\s+pay)\b", re.IGNORECASE),
    ],
}


def scan_content(text: str) -> ContentScanResult:
    """
    Scans catalog free-text fields for instruction-like injection patterns.
    Pure function, no I/O, executes in <5ms.
    
    IMPORTANT: This is informational only and sets Product.suspicious_content_flag.
    It does not authorize or block payments (structural defense handles authorization).
    """
    if not text:
        return ContentScanResult(flagged=False, matched_categories=[])

    matched_categories: List[str] = []

    for category, regex_list in PATTERNS.items():
        for pattern in regex_list:
            if pattern.search(text):
                matched_categories.append(category)
                break  # Category matched, continue to next category

    return ContentScanResult(
        flagged=len(matched_categories) > 0,
        matched_categories=matched_categories,
    )
