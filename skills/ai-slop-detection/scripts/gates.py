#!/usr/bin/env python3
"""Hard gates for binary signals (Issue #118: "Gates statt Score").

Some signals are binary facts, not score contributors: placeholder
credentials, elision comments, lorem ipsum, dead anchors. Adding them to
the weighted score dilutes calibrated dimensions. Instead they run as
gates: FAIL -> hard marking in the report, PASS -> no contribution.

Semantics ("necessary, not sufficient", cf. piyushbhattadforapps/
pseo-quality-gate): a single FAIL is a strong predictor of AI slop;
passing ALL gates guarantees nothing. Gates therefore:
  - never add to slop_score
  - never fire fp-guards (no threshold tuning possible on booleans)
  - surface as a dedicated ``gates`` list in the JSON output

Only gates with regex-clean, low-false-positive evidence are included.
Gates are auto-run for code/markup-like input; --gates forces them for
plain prose.
"""

import re

# Each gate: id, regex, hint, scope (code | markup | text)
GATE_PATTERNS = [
    {
        "id": "placeholder_credentials",
        "scope": "code",
        "regex": re.compile(
            r"(?i)\b("
            r"your[-_ ]?api[-_ ]?key|"
            r"sk-[a-z0-9]{3}|"
            r"changeme|"
            r"change[-_ ]me|"
            r"password\s*[:=]\s*['\"](?:xxx+|your|change|placeholder|secret)['\"]|"
            r"api[-_ ]?key\s*[:=]\s*['\"]?(?:xxx+|your|change|placeholder|\*{3,})['\"]?"
            r")\b"),
        "hint": "placeholder credential left in code — hard gate",
    },
    {
        "id": "elision_comments",
        "scope": "code",
        "regex": re.compile(
            r"(?://|#|/\*)\s*(?:\.\.\.|…|\\.\\.)(?:\s*(?:rest|remaining|and so on"
            r"|wie oben|restliche|weiter wie|existing code|other code|as before"
            r"|implementation|logic|details))?"
            r"|rest of (?:the )?(?:implementation|code|logic) (?:here )?\.\.\."
            r"|(?:…|\.\.\.)\s*(?:rest|weitere|Rest)"),
        "hint": "elision comment — '... rest of code' placeholder",
    },
    {
        "id": "lorem_ipsum",
        "scope": "markup",
        "regex": re.compile(r"(?i)\blorem ipsum\b|\bdolor sit amet\b"),
        "hint": "unreplaced lorem-ipsum filler",
    },
    {
        "id": "dead_anchor",
        "scope": "markup",
        "regex": re.compile(
            r"href\s*=\s*[\"'](?:#{1,2}|javascript:void\(0\)|)[\"']"),
        "hint": "dead anchor link (href=\"#\" / empty / javascript:void(0))",
    },
    {
        "id": "placeholder_image",
        "scope": "markup",
        "regex": re.compile(
            r"(?i)(?:src|href)\s*=\s*[\"']"
            r"(?:https?://(?:via\.placeholder\.com|placehold\.it|placekitten\.com"
            r"|placebear\.com|dummyimage\.com)/[^\"']*|placeholder\.(?:png|jpe?g|svg)"
            r"|image-placeholder[^\"']*)[\"']"),
        "hint": "placeholder image URL unreplaced",
    },
    {
        "id": "todo_ship_blocker",
        "scope": "text",
        "regex": re.compile(
            r"(?i)\b(?:TODO|FIXME|XXX)\b[^.\n]{0,60}"
            r"(?:before (?:launch|ship|deploy|release)|"
            r"vor (?:Launch|Release|Auslieferung)|"
            r"insert (?:your|real)|hier einfügen|einfügen)"),
        "hint": "TODO/FIXME explicitly marked as launch blocker",
    },
]

# Code/markup detection for auto-scope (kept deliberately cheap and
# conservative: auto-run only if clearly code/markup, else --gates opt-in).
_CODE_HINTS = re.compile(
    r"(?m)^\s*(?:import |from \w+ import |def |function |const |let |var |"
    r"class |<html|<!DOCTYPE|</?[a-z]+[ >]|#!/)")
_MARKUP_HINTS = re.compile(r"(?i)<(?:html|body|div|a |img |head|p>|h[1-6]>)")


def looks_like_code_or_markup(text: str) -> bool:
    """Heuristic: enough structural code/markup lines present."""
    if not text:
        return False
    lines = text.splitlines()
    hits = sum(1 for line in lines if _CODE_HINTS.search(line))
    return hits >= max(1, len(lines) // 10) or bool(_MARKUP_HINTS.search(text))


def run_gates(text: str, force: bool = False) -> dict:
    """Run all hard gates. Returns {"gates": [...], "failed": n}.

    Gates apply their scope: code/markup gates only run when the input
    looks like code/markup (or ``force`` is set). text-scope gates
    always run.
    """
    code_like = looks_like_code_or_markup(text)
    results = []
    failed = 0
    for gate in GATE_PATTERNS:
        applies = (
            gate["scope"] == "text"
            or force
            or (gate["scope"] in ("code", "markup") and code_like)
        )
        if not applies:
            continue
        matches = gate["regex"].findall(text or "")
        evidence = None
        m = gate["regex"].search(text or "")
        if m:
            evidence = m.group(0)[:80]
        status = "fail" if m else "pass"
        if m:
            failed += 1
        results.append({
            "id": gate["id"],
            "status": status,
            "hits": len(matches) if matches else 0,
            "evidence": evidence,
            "hint": gate["hint"],
        })
    return {"gates": results, "failed": failed}
