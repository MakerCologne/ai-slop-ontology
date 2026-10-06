#!/usr/bin/env python3
"""
DE-Struktur-Signale (issue #76-Backlog NEU-Items, detect-only).

Drei offene Muster aus dem DE-Coverage-Mapping (docs/de-coverage.md, #76):

  M6  HollowFazitHeading   „## Fazit“-Heading mitsubstanzlosem
                           Kurznachspann (< 30 Wörter bis zum nächsten
                           Heading oder Dateiende)
  M17 LetterStructure      Brief-/Mail-Schablonen-Marker im Artefakt
                           (Betreff: + Anrede + Grußformel; ab 2
                           Marker-Typen)
  M50 BulletCapitalization Stichpunkt-Liste in EN-Konvention: alle Items
                           großgeschrieben + Punkt am Ende, mehrheitlich
                           kurze Phrasen (keine Satz-Bullets)

Lizenz-Schutz: Konzepte nach de.wikipedia „Anzeichen für
KI-generierte Inhalte“ (Projektseite) sowie eigenen DE-Beispielen
re-deriviert; KEIN Pattern-Material aus CC-BY-SA-lizenzierten
Katalogen übernommen (vgl. docs/de-coverage.md Kopf).

DETECT-ONLY: Findings nie im numerischen Slop-Score; Konfidenz ≤ 0.65.
Sprachgate: alle Signale feuern nur auf Text, der das DE-Gate passiert
(is_german aus de_typography — dort fixture-gepinnt).

Public surface:
    hollow_fazit_heading(text) / letter_structure(text) /
    bullet_capitalization(text) -> finding | None
    find_de_structure(text) -> list[finding]
"""

import re

from de_typography import is_german

# --- M6 Fazit-Heading ohne Substanz ------------------------------------------

_RECAP_HEADINGS = ("fazit", "zusammenfassung", "fazit und ausblick",
                   "fazit & ausblick", "resümee")

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)

# Kurznachspann-Schwelle: ein Fazit-Absatz mit echter Schlussfolgerung
# bringt i. d. R. mehr als 30 Wörter mit (engine-config, fixture-gepinnt).
MIN_FAZIT_WORDS = 30


def hollow_fazit_heading(text: str):
    """M6: Recap-Heading, unter dem bis zum nächsten Heading/Ende weniger
    als MIN_FAZIT_WORDS Wörter folgen."""
    if not is_german(text):
        return None
    matches = list(_HEADING_RE.finditer(text))
    for i, m in enumerate(matches):
        title = m.group(2).strip().rstrip(":").lower()
        if title not in _RECAP_HEADINGS:
            continue
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        n_words = len(body.split())
        if n_words < MIN_FAZIT_WORDS:
            return {
                "id": "HollowFazitHeading",
                "confidence": 0.65,
                "evidence": (f"Heading „{m.group(2)}“ mit nur {n_words} "
                             f"Wörtern Nachspann (< {MIN_FAZIT_WORDS})"),
                "keep_when": ("substantieller Fazit-Absatz (>= "
                              f"{MIN_FAZIT_WORDS} Wörter eigene "
                              "Schlussfolgerung) ist legitim; nur DE-Text"),
            }
    return None


# --- M17 brief-/mailschablonen-Marker im Artefakt -----------------------------

# Anrede-Zeilen (Zeilenanfang, gefolgt von Komma oder Zeilenende)
_GREETING_RE = re.compile(
    r"^(Sehr geehrte[rn]?\s+[^\n,]+|Liebe[rn]?\s+[^\n,]+|Guten Tag|"
    r"Hallo\s+\S+)\s*,?\s*$", re.MULTILINE)

# Grußformel-Zeilen (alleinstehende Zeile)
_CLOSING_RE = re.compile(
    r"^(Mit freundlichen Grüßen|Mit besten Grüßen|Viele Grüße|"
    r"Herzliche Grüße|Beste Grüße|Liebe Grüße)\s*!?\s*$",
    re.MULTILINE | re.IGNORECASE)

# Betreff-Zeile
_SUBJECT_RE = re.compile(r"^Betreff\s*:.*$", re.MULTILINE | re.IGNORECASE)


def letter_structure(text: str):
    """M17: ≥ 2 von 3 Brief-Marker-Typen (Betreff/Anrede/Grußformel) im
    Artefakt — Briefschablone statt Zielformat-Absatztext."""
    if not is_german(text):
        return None
    found = []
    if _SUBJECT_RE.search(text):
        found.append("Betreff")
    if _GREETING_RE.search(text):
        found.append("Anrede")
    if _CLOSING_RE.search(text):
        found.append("Grußformel")
    if len(found) >= 2:
        return {
            "id": "LetterStructure",
            "confidence": 0.6,
            "evidence": (f"Brief-/Mail-Marker im Artefakt: "
                         f"{', '.join(found)}"),
            "keep_when": ("echte Korrespondenz-/Mail-Genre ist legitim "
                          "(detect-only, kein Score); nur DE-Text"),
        }
    return None


# --- M50 Stichpunkt-Listen in EN-Konvention -----------------------------------

# Liste gilt als Stichpunkt-Liste ab dieser Item-Zahl (engine-config,
# fixture-gepinnt).
MIN_BULLETS = 4
# Phrase-Bullets (keine vollständigen Sätze) sind i. d. R. kurz.
MAX_PHRASE_WORDS = 10


def bullet_capitalization(text: str):
    """M50: Alle Bullets einer Liste (>= MIN_BULLETS) großgeschrieben mit
    Punkt am Ende, mehrheitlich kurze Phrasen — EN-Konvention in
    deutschem Text (dt. Konvention: kleingeschriebene Phrasen ohne
    Endpunkt)."""
    if not is_german(text):
        return None
    for block in re.finditer(
            r"(?:^[ \t]*[-*+•]\s+.+\n?)+", text, re.MULTILINE):
        items = [ln.strip()[1:].strip()
                 for ln in block.group(0).strip().splitlines()]
        if len(items) < MIN_BULLETS:
            continue
        all_capped = all(it[:1].isupper() for it in items if it)
        all_period = all(it.endswith(".") for it in items if it)
        if not (all_capped and all_period):
            continue
        phrases = sum(1 for it in items if len(it.split()) <= MAX_PHRASE_WORDS)
        if phrases * 2 >= len(items):
            return {
                "id": "BulletCapitalization",
                "confidence": 0.55,
                "evidence": (f"{len(items)} Stichpunkte, alle groß mit "
                             f"Endpunkt, {phrases} kurze Phrasen — EN-"
                             "Konvention im DE-Text"),
                "keep_when": ("vollständige Satz-Bullets (mit Verb, länger) "
                              "sind legitim; Aufzählungen ohne Endpunkte "
                              "feuern nie; nur DE-Text"),
            }
    return None


# --- Aggregator ---------------------------------------------------------------

_FINDERS = (hollow_fazit_heading, letter_structure, bullet_capitalization)


def find_de_structure(text: str):
    """Alle DE-Struktur-Signale (detect-only) auf einen Text anwenden."""
    if not is_german(text):
        return []
    return [f for f in (finder(text) for finder in _FINDERS) if f]
