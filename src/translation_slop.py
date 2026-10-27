"""TRANSLATION-SLOP — MT-Calque-Detektion (issue #53, TranslationSlop-Klasse).

Zweiter Teil der #53-Sprach-Erweiterung (nach den Marker-Sets in
PR #295): Calques als Slop-Indikator. Ein Calque (Lehnuebersetzung)
ist die wortwoertliche Uebernahme einer fremdsprachigen Konstruktion
in die Zielsprache — das klassische Tell maschineller Uebersetzung
oder flacher LLM-Re-Generierung uebersetzter Inhalte.

Zwei Signale (beide detect-only, ADR-0001/0006 — Findings sind
advisory und gehen NICHT in den numerischen slop_score ein):

1. mt-calque-idiom-literal (0.8) — Idiome, die woertlich in die
   andere Sprache uebernommen wurden. Diese Paare sind praktisch
   unausdeutbar (weder Quell- noch Zielsprache kennt die Phrase
   idiomatisch) und damit hochpraezise:
     EN <- DE: "not the yellow of the egg", "understand only
               train station", "that is not my beer"
     DE <- EN: "regnet Katzen und Hunde", "an den falschen Baum
               bellen", "gerade vom Pferd (in den Mund?)"
2. mt-calque-lexeme (0.65) — Wort-/Syntaxebene:
     EN <- DE: Tag-Question ", or?" ("oder?"), "until soon"
               ("bis bald"), "I have N years" ("ich bin N Jahre
               alt"), "we see us" ("wir sehen uns"), "makes a
               photo" ("macht ein Foto"), "since N years"
               ("seit N Jahren" — falsches EN)
     DE <- EN: "nimm dir eine Pause" ("take a break" — korrekt:
               "mach/mach dir eine Pause")

FP-Handling (Issue-Forderung "FP-Handling" fuer legitime
Uebersetzungen):
  - Metasprachliche Kontexte (Doku/Unterricht ueber Calques/Idiome,
    Zeilen mit calque/wörtlich/literal/idiom-Markern) werden
    uebersprungen (keep_when-Negativ).
  - Code-Fences und Inline-Code werden vor der Detektion entfernt.
  - Jedes Muster ist closed-list kuratiert (keine generativen
    Regeln) — FP-Risiko bleibt damit begrenzt auf Listenpflege.

Quellen: research/slop-ontology-gap-2026-08-24/blind-spots.md BS-I*
(Calque-Diskussion), klassische MT-Fehlerkataloge (eigenstaendig
kuratiert). SSOT-Spiegel: ontology.json signals.translationSlop.
"""

import re

# ---------------------------------------------------------------------------
# Vorverarbeitung: Code-Fences / Inline-Code entfernen (FP-Quelle #1)
# ---------------------------------------------------------------------------

_FENCE = re.compile(r"```.*?```", re.S)
_INLINE_CODE = re.compile(r"`[^`\n]+`")


def _strip_code(text: str) -> str:
    text = _FENCE.sub("", text)
    return _INLINE_CODE.sub("", text)


# ---------------------------------------------------------------------------
# FP-Guard: metasprachliche Zeilen (Calque-/Idiom-Doku) ueberspringen
# ---------------------------------------------------------------------------

_KEEP_WHEN_METALINGUISTIC = re.compile(
    r"\b(?:calque|calques|wörtlich|wortwörtlich|lehnübersetzung"
    r"|literal(?:ly)? translated|idiom(?:s|atisch)?)\b",
    re.I,
)


# ---------------------------------------------------------------------------
# 1) Literale Idiom-Calques (closed-list, beide Richtungen)
# ---------------------------------------------------------------------------

# EN-Text mit woertlich uebernommenen DE-Idiomen
_IDIOM_EN_PATTERNS = [
    (re.compile(r"\bnot (?:quite\s+)?the yellow of the egg\b", re.I),
     "nicht das Gelbe vom Ei"),
    (re.compile(r"\b(?:I\s+)?understand only train station\b", re.I),
     "ich verstehe nur Bahnhof"),
    (re.compile(r"\b(?:that|this|it)?'?s? not my beer\b", re.I),
     "nicht mein Bier"),
]

# DE-Text mit woertlich uebernommenen EN-Idiomen
_IDIOM_DE_PATTERNS = [
    (re.compile(r"\bregnet (?:es\s+)?(?:Katzen und Hunde|Hunde und Katzen)\b", re.I),
     "it's raining cats and dogs"),
    (re.compile(r"\b(?:an|auf) (?:dem|den) falschen Baum\b", re.I),
     "bark up the wrong tree"),
    (re.compile(r"\bgerade(?:\s+noch)? vom Pferd\w*\b", re.I),
     "straight from the horse's mouth"),
]

_IDIOM_CONFIDENCE = 0.8


def _find_idiom_calques(text: str, findings: list) -> None:
    for lineno, line in enumerate(text.splitlines(), start=1):
        if _KEEP_WHEN_METALINGUISTIC.search(line):
            continue
        for pat, src in _IDIOM_EN_PATTERNS:
            for m in pat.finditer(line):
                findings.append((
                    "mt-calque-idiom-literal", _IDIOM_CONFIDENCE,
                    f"L{lineno}: {m.group(0)!r} (woertlich aus DE "
                    f"»{src}«, EN←DE)",
                ))
        for pat, src in _IDIOM_DE_PATTERNS:
            for m in pat.finditer(line):
                findings.append((
                    "mt-calque-idiom-literal", _IDIOM_CONFIDENCE,
                    f"L{lineno}: {m.group(0)!r} (woertlich aus EN "
                    f"»{src}«, DE←EN)",
                ))


# ---------------------------------------------------------------------------
# 2) Lexem-/Syntax-Calques (closed-list, beide Richtungen)
# ---------------------------------------------------------------------------

_LEXEME_CONFIDENCE = 0.65

_NUM = (r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|"
       r"twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
       r"nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)"
       r"(?:[- ](?:one|two|three|four|five|six|seven|eight|nine))?")

_LEXEME_EN_PATTERNS = [
    # Tag-Question ", or?" am Satzende (DE "oder?")
    (re.compile(r",\s*or\?[\"'”’)]*\s*$"),
     "Satzend-Tag », or?« (DE »oder?«, EN←DE)"),
    (re.compile(r"\buntil soon\b", re.I),
     "»until soon« (DE »bis bald«, EN←DE)"),
    (re.compile(rf"\bI have {_NUM} years(?:\s+old)?\b", re.I),
     "»I have N years« (DE »ich bin N Jahre alt«, EN←DE)"),
    (re.compile(r"\bwe see us\b", re.I),
     "»we see us« (DE »wir sehen uns«, EN←DE)"),
    (re.compile(r"\b(?:make|makes|making) a (?:photo|picture)\b", re.I),
     "»make a photo« (DE »ein Foto machen«, EN←DE)"),
    (re.compile(rf"\bsince {_NUM} years\b", re.I),
     "»since N years« (DE »seit N Jahren« — falsches EN, EN←DE)"),
]

_LEXEME_DE_PATTERNS = [
    (re.compile(r"\b[Nn]imm dir eine Pause\b"),
     "»nimm dir eine Pause« (EN »take a break«, DE←EN — korrekt: »mach eine Pause«)"),
]


def _find_lexeme_calques(text: str, findings: list) -> None:
    for lineno, line in enumerate(text.splitlines(), start=1):
        if _KEEP_WHEN_METALINGUISTIC.search(line):
            continue
        for pat, note in _LEXEME_EN_PATTERNS:
            for m in pat.finditer(line):
                findings.append((
                    "mt-calque-lexeme", _LEXEME_CONFIDENCE,
                    f"L{lineno}: {m.group(0)!r} — {note}",
                ))
        for pat, note in _LEXEME_DE_PATTERNS:
            for m in pat.finditer(line):
                findings.append((
                    "mt-calque-lexeme", _LEXEME_CONFIDENCE,
                    f"L{lineno}: {m.group(0)!r} — {note}",
                ))


# ---------------------------------------------------------------------------
# Public API (detect-only, nie score-wirksam)
# ---------------------------------------------------------------------------

class TranslationSlopClassifier:
    """Klassifiziert MT-Calque-Signale (detect-only).

    Rueckgabe: Liste von Dictionaries
    {signal_id, confidence, evidence} — advisory, ohne Score-Beitrag.
    """

    def classify_text(self, text: str) -> list:
        cleaned = _strip_code(text)
        findings: list = []
        _find_idiom_calques(cleaned, findings)
        _find_lexeme_calques(cleaned, findings)
        return [
            {"signal_id": sig, "confidence": conf, "evidence": ev}
            for sig, conf, ev in findings
        ]

    classify = classify_text  # convenience alias
