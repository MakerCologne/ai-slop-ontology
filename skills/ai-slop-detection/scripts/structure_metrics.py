#!/usr/bin/env python3
"""
Struktur-Metriken (issue #76, Teil 2, detect-only).

NEU-Kandidaten aus dem DE-Coverage-Mapping (docs/de-coverage.md):

  M60 SynonymRotation     Dieselbe Entitaet wird durch staendig wechselnde
                          Bezeichnungen aus einer Synonym-Familie umschrieben
                          (Organisation/Autor/Produkt/Nutzer) statt natuerlicher
                          Wiederholung — sprachagnostisch (DE+EN-Familien).
  M61 IsometricUnits      Struktureinheiten (Ueberschriften, Listenpunkte,
                          Absaetze) haben fast identische Laengen; von Menschen
                          geschriebene Texte streuen natuerlich.

Lizenz-Schutz: Re-Derivation der Konzepte aus de.wikipedia „Anzeichen für
KI-generierte Inhalte“ (dort: ueberstrukturierte, formelhafte, formelgleich
wirkende Gliederung) + eigene Heuristik und eigene Beispiele. KEIN Pattern-
Material aus CC-BY-SA-lizenzierten Drittkatalogen kopiert.

DETECT-ONLY: Findings erscheinen nie im numerischen Slop-Score; Konfidenz
<= 0.55. Beide Signale sind sprachagnostisch — kein DE-Gate (bewusste
Abweichung von de_typography, dokumentiert in docs/de-coverage.md).

Public surface:
    synonym_rotation(text) -> finding | None
    isometry(text) -> finding | None
    find_structure_findings(text) -> list[finding]
"""

import math
import re

# --- M60: Synonym-Familien (closed list, EN+DE gemischt) --------------------

SYNONYM_FAMILIES = {
    "organisation": [
        "unternehmen", "firma", "konzern", "betrieb", "organisation",
        "company", "firm", "enterprise", "business",
    ],
    "autor": [
        "autor", "autorin", "verfasser", "schreiber",
        "author", "writer",
    ],
    "produkt": [
        "produkt", "loesung", "angebot", "anwendung",
        "product", "solution", "offering",
    ],
    "nutzer": [
        "nutzer", "anwender", "benutzer", "kunde",
        "user", "customer", "client",
    ],
}

# Grenzen (fixture-kalibriert, tests/test_structure_metrics.py)
MIN_DISTINCT_MEMBERS = 3   # <3 = natuerliche Abwechslung, kein Fund
MIN_TOTAL_MENTIONS = 3
MIN_WORDS_ROTATION = 40    # kurze Texte: keine Aussagekraft

MIN_UNITS = 5              # <5 Einheiten = keine Stichprobe
MAX_STDEV_UNITS = 1.0      # Wortanzahl-Streuung unter 1.0 = isometrisch
MIN_WORDS_ISOMETRY = 20


def _word_count(line: str) -> int:
    return len(line.split())


def synonym_rotation(text: str):
    """M60: >= 3 verschiedene Mitglieder einer Synonym-Familie im selben
    (langen) Text. Einzeltreffer-Paar (2 Begriffe) bleibt unmarkiert —
    das ist normale menschliche Abwechslung (FP-Schutz)."""
    words = re.findall(r"[a-zA-Zäöüß]+", text.lower())
    if len(words) < MIN_WORDS_ROTATION:
        return None
    best_family, best_members = None, []
    for family, terms in SYNONYM_FAMILIES.items():
        members = [t for t in terms if t in words]
        if len(members) > len(best_members):
            best_family, best_members = family, members
    if len(best_members) < MIN_DISTINCT_MEMBERS:
        return None
    return {
        "id": "SynonymRotation",
        "confidence": 0.5,
        "evidence": (f"Synonym-Familie '{best_family}': {len(best_members)} "
                     f"verschiedene Bezeichnungen ({', '.join(best_members)}) "
                     "für dieselbe Entität statt Wiederholung"),
        "keep_when": ("Fachtexte können fest definierte Begriffs-Synonyme "
                      "nutzen; nur advisory werten, wenn zusätzlich "
                      "weitere KI-Anzeichen vorliegen (SIGNAL-DOD)."),
    }


def _structural_units(text: str) -> list:
    """Längste homogene Einheitenmenge: Markdown-Überschriften (#),
    Listenpunkte (-/*) oder Absätze — die erste mit >= MIN_UNITS."""
    lines = text.splitlines()
    units = {
        "headings": [l for l in lines if re.match(r"^#{1,6}\s+\S", l)],
        "bullets": [l for l in lines if re.match(r"^\s*[-*]\s+\S", l)],
        "paragraphs": [p for p in re.split(r"\n\s*\n", text) if p.strip()],
    }
    for kind in ("headings", "bullets", "paragraphs"):
        if len(units[kind]) >= MIN_UNITS:
            return units[kind]
    return []


def isometry(text: str):
    """M61: >= 5 Struktureinheiten mit Wortanzahl-Streuung < 1.0."""
    if len(text.split()) < MIN_WORDS_ISOMETRY:
        return None
    unit_lines = _structural_units(text)
    if len(unit_lines) < MIN_UNITS:
        return None
    counts = [_word_count(u) for u in unit_lines]
    mean = sum(counts) / len(counts)
    stdev = math.sqrt(sum((c - mean) ** 2 for c in counts) / len(counts))
    if stdev >= MAX_STDEV_UNITS:
        return None
    return {
        "id": "IsometricUnits",
        "confidence": 0.5,
        "evidence": (f"{len(counts)} Struktureinheiten mit nahezu gleicher "
                     f"Länge (Wörter: {counts}, Streuung {stdev:.2f}) — "
                     "menschliche Texte streuen natürlicher"),
        "keep_when": ("Tabellen-/Rezept-/Checklisten-Genres haben legitim "
                      "gleichförmige Einheiten; nur im Kontext weiterer "
                      "Signale werten (SIGNAL-DOD)."),
    }


def find_structure_findings(text: str) -> list:
    return [f for f in (synonym_rotation(text), isometry(text),
                        fake_analysis_appendix(text), pseudo_nuance(text))
            if f]


# --- M66: Fake-Analyse-Anhang -----------------------------------------------
# Relativ-/Appositionssatz, der einer Abstraktion eine generische
# Transformationsrolle zuschreibt, ohne Information hinzuzufuegen
# ("... ein Schritt, der die Art, wie wir X, veraendert").
FAKE_ANALYSIS_PATTERNS = [
    re.compile(r",\s(?:der|die|das|den|dem|welche[rms]?)\b[^.!?]{0,90}?"
               r"\b(?:die art, wie|ver[aä]ndert|pr[aä]gt|unterstreicht|"
               r"untermauert|definiert\s+neu|belebt)\b", re.IGNORECASE),
    re.compile(r"\b(?:which|that)\b[^.!?]{0,80}?\b(?:the way we|"
               r"redefines?|changes?|shapes?)\b", re.IGNORECASE),
]

MIN_FAKE_ANALYSIS_HITS = 2      # Einzeltreffer bleibt unmarkiert (FP-Schutz)
MIN_WORDS_FAKE_ANALYSIS = 15


def fake_analysis_appendix(text: str):
    """M66: >= 2 Analyse-Anhaenge ohne eigenen Informationsgehalt.
    Einzeltreffer ist unmarkiert — echte Analyse-Anhaenge kommen in
    Clustern (DoD-Grenzfall in tests/test_structure_rest.py)."""
    if len(text.split()) < MIN_WORDS_FAKE_ANALYSIS:
        return None
    hits = [m.group(0) for p in FAKE_ANALYSIS_PATTERNS for m in p.finditer(text)]
    if len(hits) < MIN_FAKE_ANALYSIS_HITS:
        return None
    return {
        "id": "FakeAnalysisAppendix",
        "confidence": 0.5,
        "evidence": (f"{len(hits)} Relativ-/Appositionssaetze mit "
                     f"generischer Transformationsrolle ohne neuen "
                     f"Informationsgehalt (z.B. {hits[0].strip()[:60]}…)"),
        "keep_when": ("informativ gefuellte Relativsaetze (Nennung von "
                      "Tatsaechlichkeiten) zaehlen nicht; Einzeltreffer "
                      "bleibt unmarkiert; nur advisory werten"),
    }


# --- M71: Retroaktive Scheinnuance -----------------------------------------
# Einschaerfungsmarker, die behaupten, die vorige Aussage zu praezisieren,
# sie aber nur wiederholen oder trivial abschwaechen.
PSEUDO_NUANCE_MARKERS = [
    "genauer gesagt",
    "streng genommen",
    "präziser formuliert",
    "um es genauer zu sagen",
    "to be precise",
    "strictly speaking",
    "more precisely",
]

MIN_NUANCE_MARKERS = 2           # einzelner Marker = normale Praezisierung
MIN_WORDS_NUANCE = 8


def pseudo_nuance(text: str):
    """M71: >= 2 verschiedene retroaktive Scheinnuance-Marker in einem
    Text. Ein einzelner Marker ist legitime Praezisierung und bleibt
    unmarkiert (Grenzfall)."""
    if len(text.split()) < MIN_WORDS_NUANCE:
        return None
    low = text.lower()
    found = sorted({m for m in PSEUDO_NUANCE_MARKERS if m in low})
    if len(found) < MIN_NUANCE_MARKERS:
        return None
    return {
        "id": "PseudoNuance",
        "confidence": 0.5,
        "evidence": (f"{len(found)} retroaktive Scheinnuance-Marker "
                     f"({', '.join(found)}) ohne echte Praezisierung"),
        "keep_when": ("echte Praezisierungen mit neuer Information; "
                      "einzelner Marker bleibt unmarkiert; nur advisory "
                      "werten (SIGNAL-DOD)"),
    }
