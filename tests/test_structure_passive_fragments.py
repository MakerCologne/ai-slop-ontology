"""Issue #76 M39 — Passiv-/subjektlose Fragmente /
PassiveFragmentStacking (detect-only, structure_metrics.py).

Segmente (Saetze, Bullets, Zeilen), die subjektlos mit Passiv-Auxiliar
("Wird kontinuierlich optimiert.") oder reinem Partizip
("Implemented in phase two.") beginnen — Handelnder fehlt, Aussage
wird zum passiven Fragment gestutzt.

Signal-DoD (#64): je 3 Positiv / 3 Negativ / 2 Grenz-Fixtures;
Einzeltreffer bleibt unmarkiert, Konfidenz 0.5, detect-only — nie im
numerischen Slop-Score.
"""

import os
import sys

SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

import structure_metrics as sm  # noqa: E402


# --- Positives: >= 2 subjektlose Passiv-Fragmente ---------------------------

POS1 = ("Wird kontinuierlich optimiert und an neue Rahmenbedingungen "
        "angepasst, damit alles stabil bleibt. Wird dabei vom Team stets "
        "ueberwacht und bei Bedarf sofort nachgebessert, ohne dass jemand "
        "fragen muss. Zusaetzlich wurde die Dokumentation aktualisiert, "
        "weil sie veraltet war.")

POS2 = ("Implemented in phase two and tested by the entire quality team "
        "before the big launch. Was reviewed by security and approved by "
        "management without any further discussion or delay in the whole "
        "process. The team celebrated the successful release with cake.")

POS3 = ("- Optimiert durch moderne Verfahren im Bereich der Verarbeitung\n"
        "- Erweitert mit Zusatzfunktionen fuer alle Kunden im Projekt\n"
        "- Getestet durch ein erfahrenes Team vor der Auslieferung heute\n"
        "- Dokumentiert in ausfuehrlichen Anleitungen fuer alle Nutzer")

# --- Negatives --------------------------------------------------------------

NEG1 = ("Wir bauten das Haus, gruben den Garten um und pflanzten viele "
        "Baeume. Die Kinder spielten draussen, waehrend die Hunde im Hof "
        "herumliefen und die Nachbarn beim Zaun standen und das Ergebnis "
        "ausgiebig lobten.")  # Aktiv-Prosa, 0 Fragmente

NEG2 = ("Das System wird kontinuierlich optimiert und an neue "
        "Rahmenbedingungen angepasst, damit alles stabil bleibt. Die "
        "Kinder spielten draussen, waehrend die Hunde im Hof herumliefen "
        "und die Nachbarn beim Zaun standen und das Ergebnis lobten.")  # Subjekt vor Aux

NEG3 = ("Wir prueften drei Angebote, verglichen Preise und fragten "
        "Kunden nach deren Erfahrung mit den Anbietern, bevor wir uns "
        "entschieden. Das Ergebnis dokumentierten wir, damit alle "
        "nachvollziehen koennen, wie wir gewaehlt haben und warum.")  # Handlungsprosa

# --- Boundaries -------------------------------------------------------------

BOUND1 = POS1.split(".")[0] + ". " + NEG1  # nur 1 Fragment + normale Saetze

BOUND2 = ("Wird optimiert. Wird erweitert. Das ist zu kurz fuer eine "
          "Aussage.")  # 2 Treffer aber < 30 Woerter -> Skip


def test_positives():
    for name, text in (("POS1", POS1), ("POS2", POS2), ("POS3", POS3)):
        f = sm.passive_fragment_stacking(text)
        assert f is not None, name
        assert f["id"] == "PassiveFragmentStacking"
        assert f["confidence"] <= 0.55


def test_negatives():
    for name, text in (("NEG1", NEG1), ("NEG2", NEG2), ("NEG3", NEG3)):
        assert sm.passive_fragment_stacking(text) is None, name


def test_boundaries():
    assert sm.passive_fragment_stacking(BOUND1) is None
    assert sm.passive_fragment_stacking(BOUND2) is None


def test_wiring_find_structure_findings():
    fs = sm.find_structure_findings(POS1)
    assert any(f["id"] == "PassiveFragmentStacking" for f in fs)


def test_detect_only_metadata():
    f = sm.passive_fragment_stacking(POS3)
    assert f is not None
    assert "keep_when" in f and f["keep_when"]
