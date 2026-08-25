#!/usr/bin/env python3
"""
DE-Typografie-Signale (issue #76, Teil 1, detect-only).

Quick Wins aus dem DE-Coverage-Mapping (docs/de-coverage.md, #76):

  M46 QuoteMismatch        „Text” statt „Text“ (U+201D statt U+201C als
                           deutsches Schlusszeichen)
  M47 TitleCaseHeadings    Kapitalisierte deutsche Funktionswörter
                           mittendrin in Überschriften („... Und Umsetzt“)
  M48 EnNumberFormats      Englisches Dezimalformat (2.5) oder Monats-Tag-
                           Datum (May 12, 2026) in deutschem Text;
                           Versionsnummern (v2.5, Python 3.12) sind exempt
  M49 GenitiveApostroph    Englisches Genitiv-'s an deutschen Namen
                           (Peter's); Marken-Allowlist (McDonald's)

Lizenz-Schutz: Konzepte nach de.wikipedia „Anzeichen für KI-generierte
Inhalte“ sowie eigenen DE-Beispielen re-deriviert; KEIN Pattern-Material
aus CC-BY-SA-lizenzierten Katalogen übernommen.

DETECT-ONLY: Findings nie im numerischen Slop-Score; Konfidenz ≤ 0.75.
Sprachgate: alle Signale feuern nur auf Text, der das DE-Gate passiert
(is_german) — englische Texte mit denselben Oberflächen (Peter's, 2.5,
Title Case) sind legitim und werden nie markiert.

Public surface:
    is_german(text) -> bool
    quote_mismatch(text) / title_case_headings(text) /
    en_number_formats(text) / genitive_apostrophe(text) -> finding | None
    find_de_typography(text) -> list[finding]
"""

import re

# --- DE-Sprachgate (geschlossene Funktionswortliste) ------------------------

_DE_FUNCTION_WORDS = {
    "der", "die", "das", "und", "ist", "nicht", "mit", "für", "auf",
    "eine", "ein", "von", "den", "dem", "sich", "auch", "als", "bei",
    "aus", "nach", "werden", "wird", "hat", "haben", "kann", "man",
}


def is_german(text: str) -> bool:
    """Naives, deterministisches DE-Gate: >= 3 verschiedene bzw. >= 5
    Vorkommen deutscher Funktionswörter."""
    words = re.findall(r"[a-zäöüß]+", text.lower())
    if not words:
        return False
    hits = [w for w in words if w in _DE_FUNCTION_WORDS]
    distinct = set(hits)
    return len(distinct) >= 3 or len(hits) >= 5


# --- M46 falsche deutsche Anführungszeichen ---------------------------------

_QUOTE_PAIR = re.compile(r"„([^„”“]{1,200}?)(“|”|\")")


def quote_mismatch(text: str):
    if not is_german(text):
        return None
    for m in _QUOTE_PAIR.finditer(text):
        if m.group(2) != "“":
            return {
                "id": "QuoteMismatch",
                "confidence": 0.7,
                "evidence": (f"„{m.group(1)[:40]}” — deutsches Schlusszeichen "
                             "muss U+201C (“) sein, gefunden U+201D (\”)"),
                "keep_when": ("gerade Anführungszeichen sind ein anderes "
                              "Muster; nur DE-Text (Sprachgate)"),
            }
    return None


# --- M47 englische Titel-Großschreibung -------------------------------------

# Deutsche Funktionswörter, die in Überschriften mittendrin NICHT groß
# geschrieben werden (Satzschreibung). Position: nicht Zeilenanfang.
_CAP_FUNCTION_WORDS = re.compile(
    r"(?<!^)\b(Der|Die|Das|Und|Oder|Mit|Für|Auf|Im|In|Am|Zu|Von|Bei|Den|"
    r"Dem|Des|Ein|Eine|Für)\b", re.MULTILINE)


def title_case_headings(text: str):
    if not is_german(text):
        return None
    for line in text.splitlines():
        hits = _CAP_FUNCTION_WORDS.findall(line)
        if len(hits) >= 2:
            return {
                "id": "TitleCaseHeadings",
                "confidence": 0.6,
                "evidence": (f"kapitalisierte Funktionswörter mittendrin: "
                             f"{', '.join(sorted(set(hits)))} in "
                             f"„{line.strip()[:50]}“"),
                "keep_when": ("Satzbeginn (einzelnes „Und“ am Zeilenanfang "
                              "ist Stil); nur DE-Text"),
            }
    return None


# --- M48 englisches Dezimal-/Datumsformat -----------------------------------

_VERSION_CONTEXT = re.compile(r"(?:(?i:\bversion|\bpython|\bv)\s*)$", )
_EN_DECIMAL = re.compile(r"(\d+)\.(\d{1,2})(?!\d)")
_EN_MONTH_DATE = re.compile(
    r"\b(?i:January|February|March|April|May|June|July|August|September|"
    r"October|November|December)\s+\d{1,2},?\s*\d{0,4}")


def en_number_formats(text: str):
    if not is_german(text):
        return None
    for m in _EN_MONTH_DATE.finditer(text):
        return {
            "id": "EnNumberFormats",
            "confidence": 0.6,
            "evidence": f"englisches Datumsformat „{m.group(0)}“ im DE-Text",
            "keep_when": "nur DE-Text; Ordnungszahlen (1. Mai) sind exempt",
        }
    for m in _EN_DECIMAL.finditer(text):
        start = m.start()
        prefix = text[max(0, start - 12):start]
        if _VERSION_CONTEXT.search(prefix):
            continue  # v2.5 / Python 3.12 / Version 3.1
        # Ordinalzahlen: „am 1. Mai“ — Tag gefolgt von großem Monatsnamen
        tail = text[m.end():m.end() + 12]
        if re.match(r"\s+(?i:Januar|Februar|März|April|Mai|Juni|Juli|August|"
                    r"September|Oktober|November|Dezember)", tail) and \
                len(m.group(1)) <= 2:
            continue
        return {
            "id": "EnNumberFormats",
            "confidence": 0.6,
            "evidence": (f"englisches Dezimalformat „{m.group(0)}“ "
                         "(deutsch: Komma)"),
            "keep_when": ("Versionsnummern und DE-Ordnungszahlen sind "
                          "exempt; nur DE-Text"),
        }
    return None


# --- M49 Genitiv-Apostroph ---------------------------------------------------

_BRAND_ALLOWLIST = {"mcdonald's", "levi's"}
_GENITIVE = re.compile(r"\b([A-ZÄÖÜ][a-zäöüß]{2,})'s\b")
_PLURAL_S = re.compile(r"\b\d{4}er\b")


def genitive_apostrophe(text: str):
    if not is_german(text):
        return None
    for m in _GENITIVE.finditer(text):
        token = m.group(0).lower()
        if token in _BRAND_ALLOWLIST:
            continue
        if _PLURAL_S.search(text[max(0, m.start() - 6):m.end()]):
            continue  # 1980er-Jahre-Stil ist kein Genitiv
        return {
            "id": "GenitiveApostrophe",
            "confidence": 0.65,
            "evidence": f"„{m.group(0)}“ — deutscher Genitiv ohne Apostroph",
            "keep_when": ("Marken-Allowlist (McDonald's); nur DE-Text — "
                          "englische Possessive sind korrekt"),
        }
    return None


# --- Aggregator ---------------------------------------------------------------

_FINDERS = (quote_mismatch, title_case_headings, en_number_formats,
            genitive_apostrophe)


def find_de_typography(text: str) -> list:
    return [f for f in (finder(text) for finder in _FINDERS) if f]
