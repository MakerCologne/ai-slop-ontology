"""Issue #76 M52 — Diff-verankertes Schreiben / DiffAnchoredWriting
(detect-only, structure_metrics.py).

Text verankert Aussagen in einem Diff/Patch, der im Text selbst nicht
sichtbar ist ("wie im obigen Diff geaendert" / "in the diff above") —
Schreiben ohne eigenstaendigen Kontext, verwaiste Referenz.

Signal-DoD (#64): je 3 Positiv / 3 Negativ / 2 Grenz-Fixtures;
Code-Fence/Diff-Marker im Text => Referenz verankert, kein Treffer;
Konfidenz 0.5, detect-only — nie im numerischen Slop-Score.
"""

import os
import sys

SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

import structure_metrics as sm  # noqa: E402


FENCE = "```"

# --- Positives: verwaiste Diff-Referenzen ohne sichtbaren Diff -------------

POS1 = ("Wie im obigen Diff geaendert, wird die Validierung jetzt frueher "
        "ausgefuehrt und weitere Details wurden angepasst. Die Aenderung "
        "betrifft mehrere Stellen im Patch oben und stellt sicher, dass "
        "alles konsistent bleibt.")

POS2 = ("As shown in the diff above, the validation now runs earlier and "
        "several additional details were adjusted for consistency across "
        "the whole pipeline, including its tests and documentation.")

POS3 = ("Die Implementierung folgt dem Muster aus dem Review: siehe diff "
        "oben fuer die vollstaendige Uebersicht. Weitere Stellen sind im "
        "gezeigten Patch ebenfalls beruecksichtigt worden.")

# --- Negatives --------------------------------------------------------------

NEG1 = ("Wir prueften drei Angebote, verglichen Preise und fragten Kunden "
        "nach deren Erfahrung mit den Anbietern, bevor wir uns entschieden "
        "und alles ausfuehrlich dokumentierten.")  # Handlungsprosa, 0 Referenzen

NEG2 = (FENCE + "\n" + "diff --git a/x.py b/x.py\n" + "+ neuer Code\n" + FENCE
        + "\nWie im obigen Diff geaendert, wird die Validierung jetzt "
        "frueher ausgefuehrt und weitere Details wurden entsprechend "
        "angepasst, damit alles konsistent bleibt.")  # Diff sichtbar => verankert

NEG3 = ("Der Patch enthaelt eine Aenderung der Validierung, die das Team "
        "ausfuehrlich besprochen hat, bevor alle Beteiligten dem Vorgehen "
        "zugestimmt haben.")  # "Aenderung" beschrieben, keine Diff-Referenz

# --- Boundaries -------------------------------------------------------------

BOUND1 = "Wie im Diff geaendert."  # < 20 Woerter -> Skip

BOUND2 = (FENCE + "\n" + "+ framed line\n" + FENCE + "\n"
          "Im obigen Patch wird die Validierung angepasst und vieles mehr "
          "im Detail erklaert, damit alle nachvollziehen koennen, was hier "
          "genau passiert ist.")  # 1 Referenz, aber Diff-Kontext sichtbar


def test_positives():
    for name, text in (("POS1", POS1), ("POS2", POS2), ("POS3", POS3)):
        f = sm.diff_anchored_writing(text)
        assert f is not None, name
        assert f["id"] == "DiffAnchoredWriting"
        assert f["confidence"] <= 0.55


def test_negatives():
    for name, text in (("NEG1", NEG1), ("NEG2", NEG2), ("NEG3", NEG3)):
        assert sm.diff_anchored_writing(text) is None, name


def test_boundaries():
    assert sm.diff_anchored_writing(BOUND1) is None
    assert sm.diff_anchored_writing(BOUND2) is None


def test_wiring_find_structure_findings():
    fs = sm.find_structure_findings(POS1)
    assert any(f["id"] == "DiffAnchoredWriting" for f in fs)


def test_detect_only_metadata():
    f = sm.diff_anchored_writing(POS2)
    assert f is not None
    assert "keep_when" in f and f["keep_when"]
