"""Issue #76 Rest — M29: Abbruch mittendrin (mid_sentence_break,
detect-only, structure_metrics.py).

Konzept aus docs/de-coverage.md M29 (NEU klein): Dokument bricht mitten
im Satz ab — letzte inhaltstragende Zeile ohne Satzschluss nach
abgeschlossenem Kontext, typisch fuer Token-Limit-Ausgaben.
Sprachagnostisch DE+EN (Strukturheuristik).

Signal-DoD: je 3 Positiv / 3 Negativ / 2 Grenz-Fixtures; Konfidenz 0.5,
detect-only, nie Score-wirksam.
"""

import os
import sys

SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

import structure_metrics as sm  # noqa: E402


FILL_DE = ("Dieser Absatz liefert Kontext und weitere ueberfluessige "
           "Details fuer die Messung der Kennzahlen im laufenden Projekt. ") * 3
FILL_EN = ("This paragraph provides context and further redundant detail "
           "for measuring the metrics of the current project. ") * 3


# --- M29: Abbruch mittendrin ------------------------------------------------

# Positiv 1: Artikel endet mitten im Satz auf Komma (DE)
M29_POS1 = (
    "# Bericht Q3\n\n"
    "Der Umsatz stieg im dritten Quartal deutlich an. Die Kosten blieben "
    "stabil.\n\n" + FILL_DE + "\n\n"
    "Die naechsten Schritte umfassen die Analyse der\n"
    "und darueber hinaus die"
)

# Positiv 2: EN-Dokument endet auf Praeposition (EN)
M29_POS2 = (
    "Introduction paragraph one is complete. Paragraph two also ends "
    "properly.\n\n" + FILL_EN + "\n\n"
    "We then extend the analysis to cover\n"
)

# Positiv 3: Fragment ohne Terminal nach vollstaendigen Saetzen
M29_POS3 = (
    "Einleitung mit sauberem Satz. Zweiter Satz. Dritter Satz.\n\n"
    + FILL_DE +
    "\nDer letzte Absatz beginnt mit einer neuen"
)

# Negativ 1: sauberer Satzschluss am Ende -> kein Fire
M29_NEG1 = (
    "Erster Satz endet hier. Zweiter Satz ebenfalls.\n\n" + FILL_DE +
    "Der letzte Satz endet sauber."
)

# Negativ 2: Stichpunkt-/Heading-Ende (Liste) -> Genre-Konvention, kein Fire
M29_NEG2 = (
    "# Plan\n\nAlle Punkte sind beschrieben und sauber beendet.\n\n"
    + FILL_DE +
    "- Punkt A\n"
    "- Punkt B\n"
)

# Negativ 3: Signatur-Schlusswort (E-Mail-Genre) -> kein Fire
M29_NEG3 = (
    "Vielen Dank fuer die Rueckmeldung. Ich melde mich nach dem Review.\n\n"
    + FILL_DE +
    "Viele Gruesse\n"
    "Stefan"
)

# Grenz-Fixture 1: Auslassungspunkte als bewusster Abbruch -> kein Fire
M29_BOUND1 = (
    "Erster Satz. Zweiter Satz.\n\n" + FILL_DE +
    "Fortsetzung folgt ..."
)

# Grenz-Fixture 2: kurze Notiz ohne Satzkontext (<60 Woerter) -> kein Fire
M29_BOUND2 = (
    "Einkaufsliste fuer morgen\n"
    "Milch\n"
    "Brot und dann noch"
)


def _mid(text):
    return sm.mid_sentence_break(text)


def test_pos1_comma_break_german():
    f = _mid(M29_POS1)
    assert f and f["id"] == "MidSentenceBreak" and f["confidence"] == 0.5


def test_pos2_preposition_break_english():
    f = _mid(M29_POS2)
    assert f and f["id"] == "MidSentenceBreak"


def test_pos3_fragment_without_terminal():
    f = _mid(M29_POS3)
    assert f and f["id"] == "MidSentenceBreak"


def test_neg1_clean_sentence_end():
    assert _mid(M29_NEG1) is None


def test_neg2_list_end():
    assert _mid(M29_NEG2) is None


def test_neg3_signature_word():
    assert _mid(M29_NEG3) is None


def test_boundary1_ellipsis():
    assert _mid(M29_BOUND1) is None


def test_boundary2_short_note():
    assert _mid(M29_BOUND2) is None


def test_find_structure_findings_includes_m29():
    findings = sm.find_structure_findings(M29_POS1)
    assert any(f["id"] == "MidSentenceBreak" for f in findings)
    assert all(f["confidence"] <= 0.55 for f in findings)
