"""Issue #76 M58 — Abstrakta-Stapel / NominalStyleStacking
(detect-only, structure_metrics.py).

Saetze, die Nominalisierungen stapeln (Optimierung/Verbesserung/
Implementation/coordination/…) statt Verben und Handlungen zu nennen —
Verwaltungsprosa als Struktur-Ersatz fuer Aussagen.

Signal-DoD (#64): je 3 Positiv / 3 Negativ / 2 Grenz-Fixtures;
Einzelsatz bleibt unmarkiert, Konfidenz 0.5, detect-only — nie im
numerischen Slop-Score.
"""

import os
import sys

SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

import structure_metrics as sm  # noqa: E402


# --- Positives: >= 2 Saetze mit je >= 4 Abstrakta ---------------------------

POS1 = ("Die Optimierung der Zusammenarbeit und die Verbesserung der "
        "Organisation sowie die Erweiterung der Infrastruktur bringen "
        "Effizienz und Sicherheit. Die Umsetzung der Strategie und die "
        "Evaluierung der Massnahmen sowie die Modernisierung der "
        "Verwaltung sichern die Nachhaltigkeit der Transformation.")

POS2 = ("Die Implementation der Loesung erfordert die Beruecksichtigung "
        "der Spezifikation und die Abstimmung der Konfiguration. Eine "
        "saemtliche Beruecksichtigung der Regeneration bleibt bei der "
        "Kompilation der Anwendung trotzdem die Ausnahme im Betrieb.")

POS3 = ("The implementation of the solution requires the consideration "
        "of the specification and the coordination of the migration. "
        "The evaluation of the configuration supports the modernization "
        "of the infrastructure and the improvement of communication.")

# --- Negatives --------------------------------------------------------------

NEG1 = ("Wir bauten das Haus, gruben den Garten um und pflanzten Baeume. "
        "Die Kinder spielten draussen, während die Hunde im Hof liefen "
        "und die Nachbarn beim Zaun standen und lobten das Ergebnis.")  # konkret, 0 Abstrakta-Saetze

NEG2 = ("Die Optimierung der Zusammenarbeit und die Verbesserung der "
        "Organisation sowie die Erweiterung der Infrastruktur bringen "
        "sichtbare Erleichterung. Danach ging jeder nach Hause, weil "
        "der Tag lang gewesen war und alle müde waren wie nie zuvor.")  # nur 1 Stapel-Satz

NEG3 = ("Wir prueften drei Angebote, verglichen Preise und fragten "
        "Kunden nach deren Erfahrung mit den Anbietern, bevor wir "
        "entschieden. Das Ergebnis dokumentierten wir, damit alle "
        "nachvollziehen koennen, wie wir gewaehlt haben und warum.")  # Handlungsprosa


# --- Boundaries -------------------------------------------------------------

BOUND1 = (NEG2 + " Spaeter folgte die Revision der Dokumentation und "
          "die Anpassung der Spezifikation im Rahmen der Neuausrichtung.")  # 2. Stapel-Satz -> fires

BOUND2 = ("Die Optimierung der Zusammenarbeit und die Verbesserung der "
          "Organisation bringen Effizienz. " + NEG3)  # 1 Stapel-Satz + konkreter Rest -> None


class TestNominalStyleStackingDoD:
    def test_pos1_de_stapel(self):
        f = sm.nominal_style_stacking(POS1)
        assert f is not None and f["id"] == "NominalStyleStacking"
        assert f["confidence"] <= 0.55

    def test_pos2_de_zweiter_stapel(self):
        assert sm.nominal_style_stacking(POS2) is not None

    def test_pos3_en_suffixes(self):
        assert sm.nominal_style_stacking(POS3) is not None

    def test_neg1_concrete_prose(self):
        assert sm.nominal_style_stacking(NEG1) is None

    def test_neg2_single_stacked_sentence(self):
        assert sm.nominal_style_stacking(NEG2) is None

    def test_neg3_action_prose(self):
        assert sm.nominal_style_stacking(NEG3) is None

    def test_boundary1_second_sentence_fires(self):
        f = sm.nominal_style_stacking(BOUND1)
        assert f is not None

    def test_boundary2_single_stacker_despite_length(self):
        assert sm.nominal_style_stacking(BOUND2) is None

    def test_short_text_none(self):
        assert sm.nominal_style_stacking(
            "Die Optimierung der Zusammenarbeit und Verbesserung.") is None

    def test_detect_only_never_scored(self):
        f = sm.nominal_style_stacking(POS1)
        assert set(f.keys()) >= {"id", "confidence", "evidence", "keep_when"}
        assert "score" not in f


class TestIntegration:
    def test_find_structure_findings_includes_nominal(self):
        findings = sm.find_structure_findings(POS1)
        assert any(f["id"] == "NominalStyleStacking" for f in findings)

    def test_clean_text_no_nominal_finding(self):
        text = ("Wir bauten ein Regal, schraubten es zusammen und stellten "
                "Buecher hinein. Die Familie half dabei, brachte Werkzeug "
                "mit und lachte ueber die schiefen Naegel im Holz.")
        assert not any(f["id"] == "NominalStyleStacking"
                       for f in sm.find_structure_findings(text))
