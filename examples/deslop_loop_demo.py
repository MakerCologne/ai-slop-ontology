"""DEMO-ONLY llm-free deletion fix heuristic for the DESLOP-LOOP (#51).

This is NOT a product path. ADR-0001 (detector-vs-rewriter) keeps all
rewriting out of the core; this example exists to demonstrate the injected
fix(text, findings) -> candidate callback contract with a deterministic,
network-free heuristic: it deletes matched generic phrases from the text,
budget-aware (never exceeds the 25% voice budget in one iteration).
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.deslop_loop import token_change_rate  # noqa: E402

# Small phrase list (subset of the ontology phrase DB, demo scale)
DELETE_PHRASES = [
    "in today's rapidly evolving digital landscape",
    "it's important to note that",
    "it is important to note that",
    "let's dive into",
    "serve as a testament to",
    "serves as a testament to",
    "furthermore",
    "cutting-edge",
    "robust",
    "seamless",
    "unlock your potential",
    "moreover",
    "in conclusion",
]


def deletion_fix(text: str, findings) -> str:
    """Delete known generic phrases, respecting a 25% per-iteration budget."""
    budget_cap = 0.25
    result = text
    for phrase in DELETE_PHRASES:
        candidate = re.sub(re.escape(phrase), "", result,
                           flags=re.IGNORECASE).strip()
        candidate = re.sub(r"\s{2,}", " ", candidate)
        if token_change_rate(text, candidate) <= budget_cap:
            result = candidate
    return result


# module-level alias for --fix-module consumers
fix = deletion_fix
