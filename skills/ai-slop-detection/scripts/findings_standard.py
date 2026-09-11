#!/usr/bin/env python3
"""
Findings-Standard mit Receipts (issue #119, detect-only output contract).

Community-Konsens (Slopdar / ZeroSlop --explain / hallucinot) ist
"Slop-Score mit receipts": jeder Befund ist ein benannter, zitierter,
lokalisierbarer Eintrag, den ein Mensch nachpruefen kann. Normiert:

    finding = {
        "signal_id":         str,          # stabile ID (z.B. BuzzwordHit)
        "span":              [start, end], # char offsets in den Input-Text,
                                           # None wenn nicht lokalisierbar
        "evidence_quote":    str,          # zitierte Textstelle
        "reliability":       str,          # "high" | "medium" | "low"
                                           # (+ detect-only explizit)
        "suggested_action":  str,          # naechster Schritt fuer den Menschen
    }

Design-Regeln (aus adr/0001 + #64-Disziplin):
- Der Standard ist ein AUSGABE-Vertrag, kein Score-Vertrag: kein Feld
  fliesst in slop_score ein.
- Detect-only-Befunde bleiben detect-only: reliability beschreibt die
  Beweislage, nie eine Eskalationsstufe.
- span istUTF-8-charbasiert; nicht lokalisierbare Befunde (z.B.
  dokumentglobale Metriken wie register_drift) setzen span=None und
  muessen in evidence_quote sagen, worauf sie sich beziehen.

Public surface:
    FIELDS                       -tuples of required field names
    make_finding(...)            -dict nach Standard bauen
    validate_finding(f)          -None oder raises ValueError
    span_for(text, needle)       -[start, end] oder None
    from_rhetorical(pattern)     -Adapter: rhetorical_patterns Eintrag
    from_register(finding)       -Adapter: register_profile Eintrag
    from_naturalness(finding)    -Adapter: naturalness_guard Eintrag
    findings_from_result(result, text) -Receipts aus slop_score-Ergebnis
"""

from __future__ import annotations

from typing import Optional

# Kanonische Feldreihenfolge (auch Output-Reihenfolge in JSON).
FIELDS = ("signal_id", "span", "evidence_quote", "reliability",
          "suggested_action")

RELIABILITY_LEVELS = ("high", "medium", "low")

# Voller Saetze statt blosser IDs als Handlungsempfehlung: der Receipt
# soll ohne Kontext-Doku lesbar sein (ZeroSlop-Rewrite-Hinweis-Stil).
_DEFAULT_ACTIONS = {
    "BuzzwordHit": "Marker streichen oder durch eine konkrete Aussage ersetzen.",
    "PhraseHit": "Formulierung umschreiben; AI-Phrase durch Inhalt ersetzen.",
    "AuthorityPhrase": "Beleg pruefen: Quelle nennen oder Behauptung streichen.",
    "MultilingualHit": "Marker uebersetzen/ersetzen; Sprachmix pruefen.",
    "RhetoricalPattern": "Pattern benannt pruefen; fix-Vorschlag im Eintrag.",
    "RegisterDrift": "Register vereinheitlichen oder Absaetze trennen.",
    "OverSanitized": "Advisory: pruefen, ob Eigenheiten verloren gingen.",
}

_DETECTION_HINT = (" [detect-only, kein Score-Anteil]")


def span_for(text: str, needle: str) -> Optional[list]:
    """Char-offset span [start, end) des ersten Vorkommens; None wenn
    nicht auffindbar (needle leer oder nicht enthalten)."""
    if not needle:
        return None
    idx = text.find(needle)
    if idx < 0:
        return None
    return [idx, idx + len(needle)]


def make_finding(signal_id: str,
                 evidence_quote: str,
                 span: Optional[list],
                 reliability: str,
                 suggested_action: str,
                 detect_only: bool = True) -> dict:
    """Baue und validiere einen Standard-Befund in kanonischer Feldordnung."""
    if reliability not in RELIABILITY_LEVELS:
        raise ValueError(f"reliability muss in {RELIABILITY_LEVELS} liegen: "
                         f"{reliability!r}")
    if span is not None:
        if (not isinstance(span, (list, tuple)) or len(span) != 2
                or not all(isinstance(i, int) for i in span)
                or span[0] < 0 or span[1] < span[0]):
            raise ValueError(f"span muss [start, end]-Intervall sein: {span!r}")
    action = suggested_action or _DEFAULT_ACTIONS.get(
        signal_id, "Mensch prueft den Beleg und entscheidet.")
    if detect_only and action and _DETECTION_HINT not in action:
        action = action + _DETECTION_HINT
    finding = {
        "signal_id": signal_id,
        "span": list(span) if span is not None else None,
        "evidence_quote": evidence_quote,
        "reliability": reliability,
        "suggested_action": action,
    }
    validate_finding(finding)
    return finding


def validate_finding(f: dict) -> None:
    """Wirft ValueError, wenn der Befund dem Standard widerspricht."""
    if not isinstance(f, dict):
        raise ValueError("finding muss ein dict sein")
    missing = [k for k in FIELDS if k not in f]
    if missing:
        raise ValueError(f"findings fehlen Felder: {missing}")
    extra = [k for k in f if k not in FIELDS]
    if extra:
        raise ValueError(f"unbekannte findings-Felder: {extra}")
    if not isinstance(f["signal_id"], str) or not f["signal_id"]:
        raise ValueError("signal_id muss nicht-leerer str sein")
    if not isinstance(f["evidence_quote"], str) or not f["evidence_quote"]:
        raise ValueError("evidence_quote muss nicht-leerer str sein")
    if f["reliability"] not in RELIABILITY_LEVELS:
        raise ValueError(f"reliability ungueltig: {f['reliability']!r}")
    if not isinstance(f["suggested_action"], str) or not f["suggested_action"]:
        raise ValueError("suggested_action muss nicht-leerer str sein")
    if f["span"] is not None and not (isinstance(f["span"], list)
                                      and len(f["span"]) == 2):
        raise ValueError("span muss [start, end] oder None sein")


def _conf_to_reliability(confidence: float) -> str:
    """Bestehende Confidence-Skala (0..1) auf die 3-stufige reliability
    abbilden: >=0.7 high, >=0.5 medium, sonst low."""
    if confidence >= 0.7:
        return "high"
    if confidence >= 0.5:
        return "medium"
    return "low"


def from_rhetorical(pattern: dict) -> dict:
    """Adapter: Eintrag aus rhetorical_patterns.find_rhetorical_patterns."""
    return make_finding(
        signal_id=f"RhetoricalPattern:{pattern.get('id', 'Unknown')}",
        evidence_quote=pattern.get("evidence", "") or "(no evidence captured)",
        span=None,  # evidence ist Kontextzeile, keine exakte Position
        reliability=_conf_to_reliability(pattern.get("confidence", 0.5)),
        suggested_action=pattern.get("fix", ""),
    )


def from_register(finding: dict) -> dict:
    """Adapter: register_profile.register_drift_intern Eintrag."""
    return make_finding(
        signal_id=finding.get("id", "RegisterDrift"),
        evidence_quote=finding.get("evidence", "") or "(no evidence captured)",
        span=None,  # dokumentglobale Messung, nicht lokalisierbar
        reliability="medium",
        suggested_action="Register vereinheitlichen oder Absaetze trennen.",
    )


def from_naturalness(finding: dict) -> dict:
    """Adapter: naturalness_guard Eintrag (register_drift/over_sanitized)."""
    return make_finding(
        signal_id=finding.get("id", "NaturalnessGuard"),
        evidence_quote=finding.get("evidence", "") or "(no evidence captured)",
        span=None,
        reliability="low",  # advisories sind per Definition low confidence
        suggested_action="Advisory: pruefen, ob Eigenheiten verloren gingen.",
    )


def findings_from_result(result: dict, text: str) -> list:
    """Receipts aus einem slop_score()-Ergebnis bauen.

    Abgedeckt: buzzword_hits, phrase_categories, authority_phrases,
    multilingual, register-/rhetorical-Kontextbefunde. Score-dimensionen
    (Metriken ohne Textstelle) werden bewusst KEINE receipts — der
    Standard gilt fuer Befunde, nicht fuer Messwerte.
    """
    out: list = []
    signals = result.get("signals", {}) if result else {}

    for word in signals.get("buzzword_hits", []):
        span = span_for(text, word)
        quote = word if span else f"(marker: {word})"
        out.append(make_finding("BuzzwordHit", quote, span, "high",
                                _DEFAULT_ACTIONS["BuzzwordHit"]))

    for cat, phrases in (signals.get("phrase_categories") or {}).items():
        for phrase in phrases:
            span = span_for(text, phrase)
            quote = phrase if span else f"(phrase [{cat}]: {phrase})"
            out.append(make_finding("PhraseHit", quote, span, "high",
                                    _DEFAULT_ACTIONS["PhraseHit"]))

    for phrase in signals.get("authority_phrases", []):
        span = span_for(text, phrase)
        quote = phrase if span else f"(authority: {phrase})"
        out.append(make_finding("AuthorityPhrase", quote, span, "high",
                                _DEFAULT_ACTIONS["AuthorityPhrase"]))

    for lang, words in (signals.get("multilingual") or {}).items():
        for word in words:
            span = span_for(text, word)
            quote = word if span else f"({lang}: {word})"
            out.append(make_finding("MultilingualHit", quote, span, "high",
                                    _DEFAULT_ACTIONS["MultilingualHit"]))

    ctx = (result.get("context") or {}) if result else {}
    for f in ctx.get("register_findings", []):
        out.append(from_register(f))
    for f in ctx.get("rhetorical_findings", []):
        out.append(from_rhetorical(f))
    for f in ctx.get("naturalness_findings", []):
        out.append(from_naturalness(f))
    return out
