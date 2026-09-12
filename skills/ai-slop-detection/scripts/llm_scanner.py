#!/usr/bin/env python3
"""
LLM-Zweit-Scanner — Layer 2 (issue #57, advisory only).

Vertrag: docs/loop-guards/57-llm-zweit-scanner.md

- Layer 2 GEGEN die deterministische Schicht (adr/0001): der LLM-Scan
  liefert nur Veto/Befund mit zitiertem Textabschnitt und ist NIE ein
  alleiniges Abbruchkriterium — Befunde tragen ``is_fix_trigger: False``
  und ``suggested_action: "review"`` und gehen nicht in den Score ein.
- Prompt-Rotation: >= 3 Varianten mit unterschiedlicher Frageform.
- Position-Swap: jede Variante laeuft mit vorwaerts und rueckwaerts
  sortierter Signal-Liste. Ein Befund, der nicht in >= 90 % der Laeufe
  reproduziert wird, wird auf ``stability: "unsicher"`` downgegradet
  (niedrigere Confidence, kein Fix-Trigger) statt zu feuern.
- Keine Selbstkorrektur ohne externes Feedback (Huang et al., arXiv:
  2310.05685 / 2310.01798): genau ein Pass, deterministische,
  endliche Judge-Aufrufzahl (Varianten x 2).

Der Judge ist injizierbar: ``judge(prompt: str) -> str``, erwartet wird
eine JSON-Liste ``[{"signal_id": ..., "evidence_quote": ...}]``.
Kein Netzwerk, keine Modell-API in diesem Modul — die Tests nutzen
Fake-Judges; ein echter Judge wird vom Aufrufer uebergeben.

Oeffentliche Flaeche:
    run_llm_scan(text, judge, signals=None) -> dict
    render_prompt(template, text, signals) -> str
    extract_signal_order(prompt) -> list[str]
"""

import json
import re

# --- Vertragskonstanten (SSOT-registriert) -------------------------------

# Prompt-Rotation (>= 3 Varianten, unterschiedliche Frageform UND
# unterschiedliche Reihenfolge-Instruktion). Selbst formuliert; keine
# Fremd-Prompts kopiert.
PROMPT_VARIANTS = [
    ("You are reviewing a text for slop signals.\n"
     "Signals (check in this order): {signals}\n"
     "Text:\n---\n{text}\n---\n"
     "For every signal you find, answer as a JSON list of objects "
     '{"signal_id": <one of the listed ids>, '
     '"evidence_quote": <exact quote from the text>}. '
     "If you find nothing, answer []. Answer with JSON only."),

    ("Below is a document. Determine which of the listed markers occur.\n"
     "Markers: {signals}\n"
     "Document:\n---\n{text}\n---\n"
     "Return a JSON array; each element is "
     '{"signal_id": <marker id>, "evidence_quote": '
     "<verbatim span copied from the document>}. "
     "An empty array means no markers found. JSON only, no prose."),

    ("Quality check. Read the text and report occurrences of the "
     "following patterns.\n"
     "Patterns, in order: {signals}\n"
     "Text:\n---\n{text}\n---\n"
     'Output: JSON list of {"signal_id": ..., '
     '"evidence_quote": ...} with exact quotes from the text; '
     "[] if none. No explanation, JSON only."),
]

# Bias-Akzeptanzschwelle aus dem Vertrag: Uebereinstimmung >= 0.9 bei
# getauschten Positionen; darunter Downgrade auf "unsicher".
MIN_AGREEMENT = 0.9

# Advisory-Deckel: Layer-2-Befunde sind nie score-dominant (Vertrag).
ADVISORY_MAX_CONFIDENCE = 0.5
UNSICHER_MAX_CONFIDENCE = 0.35

# Kurztext-Guard: Layer 2 lohnt sich erst ab einer Mindestlaenge.
MIN_WORDS_SCAN = 20

_SIGNAL_LIST_RE = re.compile(
    r"(?:Signals \(check in this order\):|Markers:|"
    r"Patterns, in order:)\s*(.+)", re.IGNORECASE)


def _word_count(text):
    return len(text.split())


def render_prompt(template, text, signals):
    """Fuelle eine Prompt-Variante mit Text und Signal-Reihenfolge."""
    return (template
            .replace("{signals}", ", ".join(signals))
            .replace("{text}", text))


def extract_signal_order(prompt):
    """Liest die Signal-Reihenfolge aus einem gerenderten Prompt."""
    match = _SIGNAL_LIST_RE.search(prompt)
    if not match:
        return []
    return [s.strip() for s in match.group(1).split(",") if s.strip()]


def _parse_findings(raw):
    """JSON-Antwort des Judges parsen; bei Muell -> None (kein Crash)."""
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(data, list):
        return None
    findings = []
    for item in data:
        if not isinstance(item, dict):
            return None
        sid = item.get("signal_id")
        quote = item.get("evidence_quote")
        if not isinstance(sid, str) or not isinstance(quote, str):
            return None
        findings.append({"signal_id": sid, "evidence_quote": quote})
    return findings


def _quote_in_text(quote, text):
    """Zitat muss tatsaechlich aus dem Text stammen (Belegpflicht)."""
    return bool(quote) and quote in text


def _merge_runs(runs, text):
    """Aggregiere alle Laeufe: agreement je (signal_id, quote-Treffer)."""
    total = len(runs)
    counts = {}
    for findings in runs:
        for f in findings:
            if not _quote_in_text(f["evidence_quote"], text):
                continue  # erfundenes Zitat -> verworfen
            key = f["signal_id"]
            counts.setdefault(key, []).append(f)
    merged = []
    for sid, hits in counts.items():
        agreement = len(hits) / total if total else 0.0
        # Repraesentant: laengstes Zitat (stabilste Formulierung)
        rep = max(hits, key=lambda f: len(f["evidence_quote"]))
        merged.append({
            "signal_id": sid,
            "evidence_quote": rep["evidence_quote"],
            "agreement": round(agreement, 3),
            "stability": "stable" if agreement >= MIN_AGREEMENT
            else "unsicher",
            "confidence": ADVISORY_MAX_CONFIDENCE
            if agreement >= MIN_AGREEMENT else UNSICHER_MAX_CONFIDENCE,
            "layer": "advisory",
            "is_fix_trigger": False,
            "suggested_action": "review",
        })
    merged.sort(key=lambda f: (-f["agreement"], f["signal_id"]))
    return merged


def run_llm_scan(text, judge, signals=None):
    """Ein Layer-2-Pass: Rotation + Position-Swap, genau ein Durchlauf.

    Returns dict mit status/verdict/findings/agreement-Diagnostik.
    Findings sind advisory: nie Fix-Trigger, nie Score-Eingang.
    """
    if signals is None:
        signals = ["buzzwords", "template_phrases", "moral_patterns"]
    if _word_count(text) < MIN_WORDS_SCAN:
        return {"status": "skipped_short", "verdict": "clean",
                "findings": [], "runs": 0, "parse_failures": 0}

    runs = []
    parse_failures = 0
    for template in PROMPT_VARIANTS:
        for order in (list(signals), list(reversed(signals))):
            prompt = render_prompt(template, text, order)
            raw = judge(prompt)
            parsed = _parse_findings(raw)
            if parsed is None:
                parse_failures += 1
                continue
            runs.append(parsed)

    findings = _merge_runs(runs, text)
    if parse_failures and not runs:
        return {"status": "inconclusive", "verdict": "inconclusive",
                "findings": [], "runs": 0,
                "parse_failures": parse_failures}
    verdict = "findings" if findings else "clean"
    return {
        "status": "ok",
        "verdict": verdict,
        "findings": findings,
        "runs": len(runs),
        "parse_failures": parse_failures,
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke
    import sys

    def echo_judge(prompt):
        return "[]"

    result = run_llm_scan(" ".join(["word"] * 30), echo_judge)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0)
