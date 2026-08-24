#!/usr/bin/env python3
"""
Instruction-slop analysis (issue #33) — CLAUDE.md/AGENTS.md/SKILL.md-like files.

Four detect-only signals for instruction files that an agent cannot act on:

1. generic-advice — contentless virtue words ("write clean code", "be
   thorough", "follow best practices") instead of checkable commands.
2. obvious — rules restating what the agent does by default ("use git").
3. too-vague — imperatives without a measurable object ("improve quality").
4. contradiction — "always X" and "never X" for the same X.

Public surface:
    analyze_instructions(text) -> {"signals": [{id, confidence, evidence, keep_when}]}
"""

import re

GENERIC_ADVICE = [
    "write clean code", "be thorough", "follow best practices",
    "best practices in everything", "be proactive", "think outside the box",
    "deliver high quality", "ensure high quality",
]

OBVIOUS_RULES = [
    "use git", "use version control", "commit often", "commit your changes",
    "save your work", "read the code", "use the terminal",
]

TOO_VAGUE = [
    "improve quality", "make it better", "keep it clean", "ensure quality",
    "be helpful", "do the right thing", "be smart about it",
]

_ALWAYS = re.compile(r"\balways\s+([^.\n]+)", re.IGNORECASE)
_NEVER = re.compile(r"\bnever\s+([^.\n]+)", re.IGNORECASE)


def _norm(x: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", x.lower()).strip()


def analyze_instructions(text: str) -> dict:
    lowered = text.lower()
    signals = []

    for phrase in GENERIC_ADVICE:
        if phrase in lowered:
            signals.append({
                "id": "generic-advice",
                "confidence": 0.6,
                "evidence": f'"{phrase}"',
                "keep_when": "Preamble sentences that frame genuinely "
                             "checkable rules below (rare; usually still cut).",
            })
            break

    for phrase in OBVIOUS_RULES:
        if phrase in lowered:
            signals.append({
                "id": "obvious",
                "confidence": 0.55,
                "evidence": f'"{phrase}" — restates default agent behavior',
                "keep_when": "Onboarding docs aimed at humans, not agent "
                             "instruction files.",
            })
            break

    for phrase in TOO_VAGUE:
        if phrase in lowered:
            signals.append({
                "id": "too-vague",
                "confidence": 0.6,
                "evidence": f'"{phrase}" — no measurable object',
                "keep_when": "Aspirational mission statements kept separate "
                             "from the operative rules.",
            })
            break

    always = {_norm(m.group(1)) for m in _ALWAYS.finditer(text)}
    never = {_norm(m.group(1)) for m in _NEVER.finditer(text)}
    clash = always & never
    if clash:
        first = sorted(clash)[0]
        signals.append({
            "id": "contradiction",
            "confidence": 0.8,
            "evidence": f'"always {first}" vs "never {first}"',
            "keep_when": "Different scopes stated elsewhere (e.g. different "
                         "environments) — then quote the scopes in both rules.",
        })

    return {"signals": signals}
