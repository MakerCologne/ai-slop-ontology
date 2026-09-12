"""Issue #35 (slopgh): Domain-Trigger-Metadatum je Signal (``triggered_by: domain``).

Slop-Defaults sind domain-konditional (unslop-Insight: "If the page is for
devtools -> ..."). Statische Signale ohne Domain-Kontext erzeugen
systematische False Positives/Negatives.

Zwei Semantiken (beide optional, beide dokumentiert in ontology.json
unter ``signals.domainBindings``):

``only-triggers-in``
    Das Signal ist nur in den gelisteten Domains ein sinnvoller Indikator
    ("meta_commentary" ist essay-spezifisch). Mit ``--domain D`` feuert es
    nur, wenn D gelistet ist; ohne ``--domain`` bleibt das Verhalten
    unverändert (keine Detektions-Regression durch Weglassen).

``suppressed-in``
    Das Signal ist in den gelisteten Domains Genre-Konvention und wird
    dort nicht bestraft ("marketing_cta" auf einer Landing Page).

Konfiguration only — analog genre_profiles (#42): keine Auto-Erkennung,
der Caller gibt die Domain explizit an (``--domain <name>``).
"""

from __future__ import annotations

# --- Pilot-Bindings (Issue #35: 5 Signale mit Domain-Bindung dokumentiert) ---
#
# IDs sind Phrase-Kategorien bzw. Signal-Familien wie sie der Scorer
# intern benutzt (PHRASE_CATEGORIES / Familien-Namen).
SIGNAL_DOMAIN_BINDINGS = {
    # 1) Meta-Kommentar ("in this article we'll explore") ist ein
    #    Essay-/Blog-Indikator — in Changelogs/UI-Copy kein Signal.
    "meta_commentary": {
        "triggered_by": "domain",
        "semantics": "only-triggers-in",
        "domains": ["essay", "blog", "review"],
        "rationale": "Self-referential framing is genre-defining in essays "
                     "and blogs; in changelogs or UI copy it is noise, "
                     "not a slop tell.",
    },
    # 2) CTA-Formeln sind auf Landing Pages / UI-Copy Genre-Konvention.
    "marketing_cta": {
        "triggered_by": "domain",
        "semantics": "suppressed-in",
        "domains": ["ui_copy", "landing_page"],
        "rationale": "CTA formulas ('sign up today', 'get started') are "
                     "conventional on landing pages; penalizing them there "
                     "is a systematic false positive.",
    },
    # 3) Changelogs sind per Konvention listenlastig.
    "list_heavy": {
        "triggered_by": "domain",
        "semantics": "suppressed-in",
        "domains": ["changelog", "release_notes"],
        "rationale": "Changelogs and release notes are lists by convention; "
                     "list-heaviness is not a slop signal there.",
    },
    # 4) Assistant-Signoffs sind in Support-Antworten funktional.
    "assistant_signoff": {
        "triggered_by": "domain",
        "semantics": "suppressed-in",
        "domains": ["support_reply", "chat"],
        "rationale": "'Hope this helps' is a functional closing in support "
                     "correspondence, not slop.",
    },
    # 5) Hedging ist in Rechts-/Compliance-Texten Genre-Konvention.
    "hedging_qualifiers": {
        "triggered_by": "domain",
        "semantics": "suppressed-in",
        "domains": ["legal", "compliance"],
        "rationale": "Hedged language is genre-required in legal and "
                     "compliance writing; the signal would fire on "
                     "virtually every contract.",
    },
}

KNOWN_DOMAINS = sorted({
    d for b in SIGNAL_DOMAIN_BINDINGS.values() for d in b["domains"]
})


def get_bindings() -> dict:
    """Return a copy of the pilot bindings (SSOT mirror in ontology.json)."""
    return {k: dict(v) for k, v in SIGNAL_DOMAIN_BINDINGS.items()}


def signals_inactive_in_domain(domain: str) -> set:
    """Signal-IDs, die in ``domain`` nicht feuern duerfen.

    Vereint beide Semantiken:
    - ``suppressed-in``: Domain gelistet -> inaktiv.
    - ``only-triggers-in``: Domain NICHT gelistet -> inaktiv.
    Unknown domain -> leere Menge (keine Bindings aktiv, Verhalten wie ohne
    ``--domain``); unbekannte Domains werden beim CLI-Parsing abgelehnt.
    """
    inactive = set()
    for signal_id, binding in SIGNAL_DOMAIN_BINDINGS.items():
        domains = binding["domains"]
        if binding["semantics"] == "suppressed-in":
            if domain in domains:
                inactive.add(signal_id)
        else:  # only-triggers-in
            if domain not in domains:
                inactive.add(signal_id)
    return inactive
