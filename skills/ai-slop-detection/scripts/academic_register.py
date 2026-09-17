#!/usr/bin/env python3
"""
Academic-register signals (issue #114, detect-only).

Drei invertierbare Signale fuer das Register ``academic`` (BS-I3, Quellen:
cbsteh/anti-ai-writing, arXiv:2412.11385). Jedes Signal ist **invertierbar**:
ein identischer Aussagesatz feuert NICHT, sobald die konventionalisierte
Absicherung (Zahl, Referenz, Quelle) im selben Satz steht — echte Papers
bleiben damit unangetastet (Register-Guard), slopige Texte feuern (Slop-Signal).

Doppelte Verwendung (#114):
  1. Slop-Signal in fremden Texten (Reporting, never scored — ADR-0001).
  2. Register-Guard: fuer genre=academic wird nur gemeldet, was auch ein
     echtes Paper nicht enthalten wuerde (fehlende Absicherung).

Signale:

1. EpistemicMismatch — starkes epistemisches Verb (demonstrate/prove/
   confirm) im selben Satz wie hedge-qualifizierte Datenlage
   (may/might/suggest/appears). Positive Behauptung ueber hedgierte
   Evidenz = Registerbruch. Inversion: Hedge alleine ODER starkes Verb
   mit Quantifizierung -> kein Finding.
2. UnquantifiedScopeClaim — "comprehensive analysis/survey/study" ohne
   Zahl (n=, Anzahl, Zeitraum, Spanne) im selben Satz. Deterministisch
   pruefbar. Inversion: "comprehensive survey of 214 papers (2018-2025)"
   -> kein Finding.
3. VagueAttribution — "the literature suggests" / "studies show" /
   "research indicates" ohne Zitatmarker im selben Satz. Inversion: mit
   ([12], (Smith et al., 2020), \\cite{...}) -> kein Finding.

Public surface:
    find_academic_register_findings(text, genre=None) -> [finding]
    ACADEMIC_REGISTER -> {id: {keep_when, example_slop, example_fix}}
"""

import re

import tokenizer

# --- Wortlisten (self-derived, EN) -------------------------------------------

# Starke epistemische Verben: Behauptung ueber die Datenlage, die Belege
# verlangt (COLING-2025-Evidenz: LLMs upcast hedges zu demonstrations).
STRONG_EPISTEMIC = [
    r"\bdemonstrates?\b", r"\bdemonstrated\b",
    r"\bproves?\b", r"\bproven\b",
    r"\bconclusively\s+shows?\b",
    r"\bconfirms?\b", r"\bconfirmed\b",
    r"\bestablishes?\b",
]

# Hedge-Marker: quali­fizierte, unsichere Datenlage.
HEDGE_MARKERS = [
    r"\bmay\b", r"\bmight\b", r"\bappears?\b", r"\bseems?\b",
    r"\bsuggests?\b", r"\bindicates?\b", r"\bpossible\b", r"\bpreliminary\b",
    r"\bpotentially\b", r"\bin\s+some\s+cases\b",
]

# Scope-Claim-Substantive mit Anspruch auf Vollstaendigkeit.
SCOPE_CLAIMS = [
    r"\bcomprehensive\s+(?:analysis|survey|study|review|overview|evaluation)\b",
    r"\bexhaustive\s+(?:analysis|survey|study|review|list)\b",
    r"\ball\s+(?:relevant|existing|available)\s+(?:studies|literature|work)\b",
]

# Quantifizierungs-Marker: Zahl, n=, Zeitraum, Spanne, "of the N".
QUANTIFIERS = [
    r"\bn\s*=\s*\d+",                       # n = 42
    r"\b\d+\s+(?:papers?|studies?|articles?|participants?|subjects?|"
    r"patients?|records?|samples?|responses?|documents?|datasets?|models?|"
    r"repositories?)\b",                     # 214 papers
    r"\b(?:between|from|across)\s+\d{4}\s*(?:-|–|—|to)\s*\d{4}\b",  # 2018-2025
    r"\bin\s+\d{4}\b",                       # in 2023
    r"\b\d{2,3}\s*(?:%|percent)\b",          # 87 % of cases
    r"\brange(?:d|s)?\s+(?:from\s+)?[\d.]+\s*(?:to|-|–)\s*[\d.]+",
]

# Zitatmarker: numerisch, Autor-Jahr, LaTeX.
CITATION_MARKERS = [
    r"\[\d{1,3}\]",                          # [12]
    r"\[\d{1,3},\s*\d{1,3}\]",               # [12, 34]
    r"\(\s*[A-ZÄÖÜ][^()]{0,60}\b(?:19|20)\d{2}[a-z]?\s*\)",      # (Smith et al., 2020)
    r"\\cite\{[^}]{1,80}\}",                 # \cite{smith2020}
    r"\\citep?\s*\[[^\]]{1,40}\]\{[^}]{1,80}\}",
    r"\bsee\s+(?:also\s+)?(?:Section|Table|Figure|Appendix)\s+[A-Z0-9]",
]

_MIN_WORDS = 40  # kuerzer als ein Abstract-Fragment: keine Aussagekraft


def _sentences(text: str) -> list:
    return [s for s in tokenizer.split_sentences(text) if s.strip()]


def _any(patterns: list, s: str) -> bool:
    return any(re.search(p, s, flags=re.IGNORECASE) for p in patterns)


# --- Signal 1: EpistemicMismatch ---------------------------------------------

def _epistemic_mismatch(sentences: list):
    hits = [s.strip() for s in sentences if _any(STRONG_EPISTEMIC, s)
            and _any(HEDGE_MARKERS, s)]
    if not hits:
        return None
    return {
        "id": "EpistemicMismatch",
        "confidence": 0.5,
        "evidence": ("Starkes epistemisches Verb und Hedge-Qualifier im selben "
                     "Satz: " + hits[0][:120]),
        "keep_when": ("Hedge ohne starkes Verb (korrekt vorsichtig); starkes "
                      "Verb mit Quantifizierung/N im selben Satz (belegte "
                      "Staerke); Zitate mit [n]/Autor-Jahr; methodische "
                      "Limitations-Absaetze ('this may indicate')"),
    }


# --- Signal 2: UnquantifiedScopeClaim ----------------------------------------

def _unquantified_scope_claim(sentences: list):
    hits = []
    for s in sentences:
        if _any(SCOPE_CLAIMS, s) and not _any(QUANTIFIERS, s):
            hits.append(s.strip())
    if not hits:
        return None
    return {
        "id": "UnquantifiedScopeClaim",
        "confidence": 0.55,
        "evidence": ("Vollstaendigkeits-Claim ohne Zahl/Zeitraum im selben "
                     "Satz: " + hits[0][:120]),
        "keep_when": ("Claim MIT n=/Anzahl/Zeitraum im selben Satz; "
                      "Quantifizierung im Folgesatz ('... 214 papers, "
                      "published 2018-2025'); Titel/Abstract-Konvention "
                      "mit Zahlen; Meta-Texte, die bewusst skizzieren"),
    }


# --- Signal 3: VagueAttribution ----------------------------------------------

def _vague_attribution(text: str):
    # Satzweises Pruefen wuerde an "et al." zerreissen (tokenizer trennt
    # dort); daher Fenster um jede Attribution im Rohtext (+-120 Zeichen).
    combined = re.compile("(?:" + "|".join(_VAGUE_ATTRIBUTIONS) + ")",
                          flags=re.IGNORECASE)
    window = 120
    hits = []
    for m in combined.finditer(text):
        ctx = text[max(0, m.start() - window):m.end() + window]
        if not _any(CITATION_MARKERS, ctx):
            hits.append(ctx.strip())
    if not hits:
        return None
    return {
        "id": "VagueAttribution",
        "confidence": 0.5,
        "evidence": ("Attribution an 'die Literatur/Forschung' ohne "
                     "Zitatmarker im selben Satz: " + hits[0][:120]),
        "keep_when": ("Satz MIT [n]/Autor-Jahr/\\cite; Verweis auf eigene "
                      "Daten ('our measurements show'); etablierte "
                      "Grundlagen ('Newton's laws') mit Lehrbuchverweis im "
                      "Kontext; einleitende Meta-Aussagen zum Paper selbst"),
    }


_VAGUE_ATTRIBUTIONS = [
    r"\bthe\s+literature\s+(?:suggests?|shows?|indicates?|reports?)\b",
    r"\bstudies\s+(?:show|suggest|indicate|have\s+shown|report)\b",
    r"\bresearch\s+(?:shows?|suggests?|indicates?)\b",
    r"\bit\s+is\s+well\s+(?:established|known|documented)\s+that\b",
    r"\bmany\s+(?:researchers?|scholars?|experts?)\s+(?:agree|argue|"
    r"have\s+(?:noted|argued))\b",
]


# --- Registry (gleiches Schema wie micro_patterns/chat_artifacts) ------------

ACADEMIC_REGISTER = {
    "EpistemicMismatch": {
        "keep_when": "Hedge ohne starkes Verb; starkes Verb mit n=/"
                     "Quantifizierung im selben Satz; zitierte Staerke",
        "example_slop": "These results demonstrate that the approach may "
                        "improve accuracy.",
        "example_fix": "These results suggest that the approach may improve "
                       "accuracy (n = 214, +3.2 %, p < .05).",
    },
    "UnquantifiedScopeClaim": {
        "keep_when": "Claim mit Anzahl/Zeitraum im selben Satz",
        "example_slop": "We provide a comprehensive analysis of the field.",
        "example_fix": "We analyze 214 papers published 2018-2025.",
    },
    "VagueAttribution": {
        "keep_when": "Satz mit [n]-, Autor-Jahr- oder \\cite-Zitat",
        "example_slop": "The literature suggests that this method "
                        "outperforms baselines.",
        "example_fix": "Prior work reports gains over baselines "
                       "(Smith et al., 2020; Jones, 2019).",
    },
}


# --- Public surface -----------------------------------------------------------

def find_academic_register_findings(text: str, genre: str = None) -> list:
    """Detect-only academic-register findings (never scored).

    ``genre`` is accepted for interface symmetry with other detect-only
    groups; the signals are already inverted (conventional academic
    phrasing WITH evidence never fires), so no genre suppression is needed.
    """
    if len(text.split()) < _MIN_WORDS:
        return []
    sentences = _sentences(text)
    findings = []
    for detector in (lambda s: _epistemic_mismatch(s),
                     lambda s: _unquantified_scope_claim(s),
                     lambda _s: _vague_attribution(text)):
        f = detector(sentences)
        if f:
            findings.append(f)
    return findings


if __name__ == "__main__":
    import json
    import sys
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("file", help="Text file to analyze (or - for stdin)")
    ap.add_argument("--genre", default=None)
    args = ap.parse_args()
    raw = sys.stdin.read() if args.file == "-" else open(
        args.file, encoding="utf-8").read()
    print(json.dumps(find_academic_register_findings(raw, genre=args.genre),
                     indent=2, ensure_ascii=False))
