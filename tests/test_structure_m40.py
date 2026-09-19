"""Issue #76 Rest — M40: Wenn-Klausel-Stapel (conditional_stacking,
detect-only, structure_metrics.py).

Konzept aus docs/de-coverage.md M40 (NEU): Aufgeblaefte Bedingungs-
architektur — ein Satz mit >= 3 gestapelten Konditionalklauseln oder
>= 3 aufeinanderfolgende Saetze, die je mit einer Konditionalklausel
beginnen, als Struktur-Ersatz fuer direkte Aussagen.
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


FILL_DE = ("Dieser Absatz liefert Kontext und weitere Details fuer die "
           "Messung der Kennzahlen im laufenden Projekt. ") * 2
FILL_EN = ("This paragraph provides context and further detail for "
           "measuring the metrics of the current project. ") * 2


def _cond(text):
    return sm.conditional_stacking(text)


# --- M40: Wenn-Klausel-Stapel ------------------------------------------------

# Positiv 1: ein Satz mit 3 gestapelten wenn-Klauseln (DE)
M40_POS1 = (
    "Einleitung fuer den Kontext dieses Absatzes. " + FILL_DE +
    "Wenn die Nachfrage steigt, und wenn die Lieferketten stabil bleiben, "
    "falls zudem die Kosten sinken, dann expandiert das Unternehmen "
    "naechstes Jahr."
)

# Positiv 2: EN — 3 aufeinanderfolgende Saetze je mit if-Klausel
M40_POS2 = (
    "Introduction sentence for context. " + FILL_EN +
    "If demand increases, revenue grows. "
    "If costs stay low, margins improve. "
    "If markets remain stable, expansion follows."
)

# Positiv 3: DE — sofern/falls-Mix, 3 aufeinanderfolgende Konditionalsaetze
M40_POS3 = (
    "Kontextsatz fuer die Messung. " + FILL_DE +
    "Sofern die Server ausreichen, skaliert die Anwendung. "
    "Falls der Traffic sinkt, reduziert das System die Instanzen. "
    "Wenn ein Fehler auftritt, leitet der Proxy um."
)

# Negativ 1: einzelne Bedingung -> normale Sprache, kein Fire
M40_NEG1 = (
    "Einleitung mit Kontext. " + FILL_DE +
    "Wenn die Nachfrage steigt, expandiert das Unternehmen."
)

# Negativ 2: zwei Bedingungen in einem Satz -> noch normale Sprache
M40_NEG2 = (
    "Einleitung mit Kontext. " + FILL_DE +
    "Wenn die Nachfrage steigt und falls die Kosten sinken, dann "
    "expandiert das Unternehmen."
)

# Negativ 3: zu kurzer Text -> keine Aussagekraft
M40_NEG3 = "Wenn X gilt und wenn Y gilt, falls Z zutrifft, dann passiere."

# Grenzfall 1: 2 aufeinanderfolgende Konditionalsaetze -> unter Schwelle
M40_BOUND1 = (
    "Einleitung mit Kontext. " + FILL_DE +
    "Wenn der Timer ablaeuft, bricht die Session ab. "
    "Falls der Nutzer erneut klickt, startet sie neu. "
    "Danach werden alle offenen Handles freigegeben."
)

# Grenzfall 2: 3 Konditionalsaetze, aber nicht aufeinanderfolgend -> kein Fire
M40_BOUND2 = (
    "Einleitung mit Kontext. " + FILL_DE +
    "Wenn der Timer ablaeuft, bricht die Session ab. "
    "Der Nutzer wird darueber informiert und kann neu starten. "
    "Falls der Cache voll ist, wird er geleert. "
    "Anschliessend laeuft der Dienst weiter. "
    "Sofern Ressourcen fehlen, loggt das System einen Fehler."
)


def test_pos1_three_stacked_german():
    f = _cond(M40_POS1)
    assert f and f["id"] == "ConditionalStacking"


def test_pos2_three_consecutive_english():
    f = _cond(M40_POS2)
    assert f and f["id"] == "ConditionalStacking"


def test_pos3_three_consecutive_german_mixed():
    f = _cond(M40_POS3)
    assert f and f["id"] == "ConditionalStacking"


def test_neg1_single_condition():
    assert _cond(M40_NEG1) is None


def test_neg2_two_conditions():
    assert _cond(M40_NEG2) is None


def test_neg3_too_short():
    assert _cond(M40_NEG3) is None


def test_boundary1_two_consecutive():
    assert _cond(M40_BOUND1) is None


def test_boundary2_non_consecutive():
    assert _cond(M40_BOUND2) is None


def test_find_structure_findings_includes_m40():
    findings = sm.find_structure_findings(M40_POS1)
    assert any(f["id"] == "ConditionalStacking" for f in findings)
    assert all(f["confidence"] <= 0.55 for f in findings)
