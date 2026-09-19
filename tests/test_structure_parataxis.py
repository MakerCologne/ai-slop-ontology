"""Issue #76 Rest — M51 Parataxe-Haeufung / ParataxisStacking
(detect-only, structure_metrics.py).

Aneinanderreihung kurzer Hauptsatz-Strukturen ohne Unterordnung als
generiertes Stakkato: mehrere Saetze mit je >= 4 rein koordinierten
Segmenten (Komma / und / oder / aber / doch / and / or / but / yet),
kein Nebensatz-Bau (Subordinator-Gate).

Signal-DoD (#64): je 3 Positiv / 3 Negativ / 2 Grenz-Fixtures;
Einzelsatz bleibt unmarkiert (advisory-Grenze, Kollisionsdisziplin
#46), Konfidenz 0.5, detect-only — nie im numerischen Slop-Score.
"""

import os
import sys

SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

import structure_metrics as sm  # noqa: E402


# --- Positives: >= 2 Parataxe-Stakkato-Saetze -------------------------------

POS1 = ("Es kam, es ging, es blieb, es endete. Wir sahen die Lage, wir "
        "prueften die Zahlen, wir zoegerten kurz, wir entschieden dann "
        "rasch und entschieden. Der Eindruck blieb zwiespaeltig und "
        "bleibt damit erwaehnenswert fuer den weiteren Verlauf.")

POS2 = ("Die Lage war klar, die Mittel fehlten, die Zeit drangte, die "
        "Lage blieb trotzdem stabil. Man diskutierte die Optionen, man "
        "verwarf die Alternativen, man einigte sich auf den Kompromiss, "
        "man vertagte den Rest auf spaeter.")

POS3 = ("It came, it stayed, it grew, it faded. The team shipped the "
        "release, the team fixed the bugs, the team wrote the notes, "
        "the team moved on to the next quarter.")

# --- Negatives -------------------------------------------------------------

NEG1 = ("Wir kamen, wir sahen, wir siegten.")  # Einzelsatz + zu kurz
NEG2 = ("Die Analyse zeigt, dass die Zahlen stimmen, weil sie mehrfach "
        "geprueft wurden. Die Brigade blieb skeptisch und vertagte die "
        "Entscheidung, weil weitere Belege fehlten.")  # Subordination
NEG3 = ("Der Bericht ist knapp. Er nennt Fakten, er nennt Zahlen, er "
        "nennt Quellen, er nennt Namen. Der Rest bleibt Kommentar und "
        "bleibt damit die Ausnahme in dieser Reihe von Saetzen.")  # 1 Satz

# --- Boundaries ------------------------------------------------------------

BOUND1 = NEG3 + " Der Anhang listet Optionen auf."  # weiterhin 1 Satz -> None
BOUND2 = (NEG1 + " Die Sonne ging auf, der Wind legte sich, die Strassen "
          "wurden leer, die Stadt wurde still. Die Leute gingen heim, die "
          "Lichter gingen aus, die Nacht kam schnell und der Tag endete.")  # 2 Saetze -> fires


class TestParataxisStackingDoD:
    def test_pos1_de_stakkato(self):
        f = sm.parataxis_stacking(POS1)
        assert f is not None and f["id"] == "ParataxisStacking"
        assert f["confidence"] <= 0.55

    def test_pos2_de_koordiniert(self):
        assert sm.parataxis_stacking(POS2) is not None

    def test_pos3_en_staccato(self):
        assert sm.parataxis_stacking(POS3) is not None

    def test_neg1_einzelsatz_kurz(self):
        assert sm.parataxis_stacking(NEG1) is None

    def test_neg2_subordination(self):
        assert sm.parataxis_stacking(NEG2) is None

    def test_neg3_ein_parataxe_satz(self):
        assert sm.parataxis_stacking(NEG3) is None

    def test_bound1_still_ein_satz(self):
        assert sm.parataxis_stacking(BOUND1) is None

    def test_bound2_zweiter_satz_fires(self):
        f = sm.parataxis_stacking(BOUND2)
        assert f is not None and f["confidence"] <= 0.55

    def test_find_structure_findings_includes_parataxis(self):
        findings = sm.find_structure_findings(POS1)
        assert any(f["id"] == "ParataxisStacking"
                   for f in sm.find_structure_findings(POS2))
        assert isinstance(findings, list)
