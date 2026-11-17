"""DE-SURFACE — 4 deterministische DE-Quick-Wins (issue #73, Punkt 3).

DE-Signallayer Pilot: sprachgebundene Oberflaechen-Signale, die der
EN-kanonische Kern nicht abdeckt. Alle Signale sind DE-gegated (das
Dokument muss klar deutsch sein) und detect-only (ADR-0001/0006).

1. de-mismatched-quotes — falsche Anfuehrungszeichen:
   „X„ (U+201E oeffnet UND schliesst), 'X' Analog, oder ein
   allein stehendes „ (Oeffner ohne U+201C-Schluss auf der Zeile).
2. de-genitive-apostroph — anglophoner Genitiv/Deppenapostroph in
   deutschem Text: "Peter's Hund", "die Pizza's" ('s / 's / 's).
3. de-us-format — US-Formate in deutschem Text: Datum M/D/YYYY
   (Tag > 12 beweist US-Reihenfolge) und Punkt-Dezimal vor
   deutschen Einheiten (3.5 kg statt 3,5 kg).
4. de-title-case — Title Case in deutschen Ueberschriften: >= 2
   mid-heading Vorkommen von im Deutschen NIE substantivischen
   Funktionswoertern in Grossschreibung ("... Und Neue Wege ...").

DETECT-ONLY: Findings sind advisory mit zitiertem Beleg und gehen
NICHT in den numerischen slop_score ein (ADR-0006). Regex-Katalog ist
eine corpus-kalibrierte Inline-Liste (dokumentierte bewusste
Abweichung von der ontology.json-SSOT-Projektion, siehe
scripts/check_ssot.py) — der SSOT-Spiegel lebt in ontology.json
`signals.deSurface` fuer Katalog-Paritaet.

Quellen: de.wikipedia „Anzeichen fuer KI-generierte Inhalte“
(CC BY-SA 4.0, eigenstaendig re-deriviert, kein Copy von
humanizer-de — deren NOTICE.md steht unter ShareAlike), issue #73.
"""

import re

# ---------------------------------------------------------------------------
# DE-Gate: Dokument gilt als deutsch ab >= 3 verschiedenen dt. Funktionswortern
# ---------------------------------------------------------------------------

_DE_FUNCTION_WORDS = {
    "der", "die", "das", "und", "ist", "nicht", "mit", "für", "auf",
    "eine", "einem", "einen", "einer", "dem", "den", "des", "von", "zu",
    "zum", "zur", "sich", "oder", "als", "auch", "werden", "wird",
    "wurde", "hat", "haben", "war", "im", "in", "am", "bei", "nach",
    "über", "unter", "aus", "dass", "wenn", "aber", "noch", "nur",
    "man", "kann", "muss", "soll", "sehr", "mehr", "immer", "durch",
}

_DE_GATE_MIN_DISTINCT = 3


def _looks_german(text: str) -> bool:
    words = re.findall(r"[a-zäöüß]{2,}", text.lower())
    return len(_DE_FUNCTION_WORDS.intersection(words)) >= _DE_GATE_MIN_DISTINCT


# ---------------------------------------------------------------------------
# 1) Falsche Anfuehrungszeichen
# ---------------------------------------------------------------------------

# „X„  — U+201E oeffnet und schliesst (Deckt auch „X" mit U+201D? Nein:
# U+201D als Schluss nach „ ist in DE falsch (korrekt: „X“ U+201C).)
_MISMATCHED_QUOTE_PATTERNS = [
    # „...“ ist korrekt; hier: „ oeffnet und „ schliesst
    re.compile(r"„[^„“”\n]{1,80}„"),
    # „ oeffnet, U+201D (engl. closing) schliesst
    re.compile(r"„[^„“”\n]{1,80}”"),
    # ‚ oeffnet und schliesst (single low quote)
    re.compile(r"‚[^‚‘’\n]{1,60}‚"),
    # ‚ oeffnet, U+201D fehlt: ‚...” 
    re.compile(r"‚[^‚‘’\n]{1,60}”"),
]

# allein stehender „-Oeffner ohne U+201C-Schluss auf derselben Zeile
_DANGLING_OPENER = re.compile(r"„")


def _find_mismatched_quotes(text: str, findings: list) -> None:
    for lineno, line in enumerate(text.splitlines(), start=1):
        for pat in _MISMATCHED_QUOTE_PATTERNS:
            for m in pat.finditer(line):
                findings.append((
                    "de-mismatched-quotes", 0.6,
                    f"L{lineno}: {m.group(0)[:60]!r}",
                ))
        # dangling „: Oeffner ohne „“-Paar-Schluss auf der Zeile
        openers = line.count("„")
        if openers and not line.count("“"):
            m = _DANGLING_OPENER.search(line)
            if m:
                start = max(0, m.start() - 20)
                findings.append((
                    "de-mismatched-quotes", 0.5,
                    f"L{lineno}: unverpaarter „-Oeffner: "
                    f"{line[start:m.start() + 40]!r}",
                ))


# ---------------------------------------------------------------------------
# 2) Genitiv-Apostroph ("Peter's Hund", "die Pizza's")
# ---------------------------------------------------------------------------

_GENITIVE_APOSTROPHE = re.compile(
    r"\b(?:[A-ZÄÖÜ][a-zäöüß]{2,}|[a-zäöüß]{3,})(?:'|’|‘)s\b"
)

# FP-Schutz: klar englische Kontexte (eigene Zitate/Code/IDs)
_KEEP_WHEN_ENGLISH_LINE = re.compile(
    r"(?:the|this|that|it'?s|let'?s|john'?s|james'?s|windows|node'?s)\b",
    re.I,
)


def _find_genitive_apostrophe(text: str, findings: list) -> None:
    for lineno, line in enumerate(text.splitlines(), start=1):
        if _KEEP_WHEN_ENGLISH_LINE.search(line):
            continue
        for m in _GENITIVE_APOSTROPHE.finditer(line):
            findings.append((
                "de-genitive-apostroph", 0.5,
                f"L{lineno}: {m.group(0)!r}",
            ))


# ---------------------------------------------------------------------------
# 3) US-Formate in deutschem Text
# ---------------------------------------------------------------------------

# M/D/YYYY mit Tag > 12 beweist US-Reihenfolge (z.B. 12/25/2026)
_US_DATE = re.compile(
    r"\b(0?[1-9]|1[0-2])/(1[3-9]|[2-3]\d)/(?:\d{2}|\d{4})\b"
)

# Punkt-Dezimal direkt vor dt. Einheiten ("3.5 kg" statt "3,5 kg")
_DOT_DECIMAL_DE_UNIT = re.compile(
    r"\b\d+\.\d+\s?(?:kg|km|cm|mm|ml|°C|Prozent|Millionen|Meter)\b",
    re.I,
)

# FP-Schutz: Versionsnummern/IP-aehnliches ("v3.5", "10.0.1")
_KEEP_WHEN_VERSION = re.compile(r"\b[vV]\d+\.\d+|\d+\.\d+\.\d+")


def _find_us_format(text: str, findings: list) -> None:
    for lineno, line in enumerate(text.splitlines(), start=1):
        for m in _US_DATE.finditer(line):
            findings.append((
                "de-us-format", 0.7,
                f"L{lineno}: US-Datum {m.group(0)!r} (DE: TT.MM.JJJJ)",
            ))
        for m in _DOT_DECIMAL_DE_UNIT.finditer(line):
            span = line[max(0, m.start() - 16):m.end() + 4]
            if _KEEP_WHEN_VERSION.search(span):
                continue
            findings.append((
                "de-us-format", 0.6,
                f"L{lineno}: {m.group(0)!r} (DE-Dezimal: Komma)",
            ))


# ---------------------------------------------------------------------------
# 4) Title Case in deutschen Ueberschriften
# ---------------------------------------------------------------------------

# Woerter, die im Deutschen NIE grossgeschrieben werden (ausser
# Satzanfang) — Prapositionen, Konjunktionen, Verben, Partikel.
_NEVER_CAPITALIZED = {
    "Und", "Oder", "Aber", "Auch", "Nicht", "Sehr", "Als", "Wie",
    "Ist", "Sind", "Wird", "Werden", "Wurde", "Wurden", "Hat",
    "Haben", "Hatte", "Kann", "Muss", "Soll", "Mit", "Für", "Von",
    "Zu", "Zum", "Zur", "Im", "In", "Am", "Auf", "Aus", "Bei",
    "Durch", "Gegen", "Ohne", "Um", "Über", "Unter", "Nach", "Vor",
    "Noch", "Nur", "Man", "Immer", "Mehr", "Ganz", "Viel", "Denn",
    "Weil", "Dass", "Wenn", "Ob",
}

_HEADING = re.compile(r"^\s{0,3}(?:#{1,6}\s+.+|=.+\s*=)$")
_MIN_HITS = 2


def _find_title_case(text: str, findings: list) -> None:
    for lineno, line in enumerate(text.splitlines(), start=1):
        if not _HEADING.match(line.rstrip()):
            continue
        words = re.findall(r"[A-Za-zÄÖÜäöüß]+", line)
        hits = [w for i, w in enumerate(words)
                if i > 0 and w in _NEVER_CAPITALIZED]
        if len(hits) >= _MIN_HITS:
            findings.append((
                "de-title-case", 0.6,
                f"L{lineno}: {line.strip()[:70]!r} "
                f"(Title-Case-Tells: {', '.join(hits[:4])})",
            ))


# ---------------------------------------------------------------------------
# Public API (detect-only, nie score-wirksam)
# ---------------------------------------------------------------------------

class DeSurfaceClassifier:
    """Klassifiziert deutsche Oberflaechen-Signale (detect-only).

    Rueckgabe: Liste von Dictionaries
    {signal_id, confidence, evidence} — advisory, ohne Score-Beitrag.
    """

    def classify_text(self, text: str) -> list:
        if not _looks_german(text):
            return []
        findings: list = []
        _find_mismatched_quotes(text, findings)
        _find_genitive_apostrophe(text, findings)
        _find_us_format(text, findings)
        _find_title_case(text, findings)
        return [
            {"signal_id": sig, "confidence": conf, "evidence": ev}
            for sig, conf, ev in findings
        ]

    classify = classify_text  # convenience alias
