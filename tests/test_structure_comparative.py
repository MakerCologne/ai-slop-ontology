"""Issue #75 Signal 6 — Komparativ-Rahmung / ComparativeFraming
(detect-only, structure_metrics.py).

Kontrastframes als Beschreibungsersatz: "weniger X als vielmehr Y",
"eher X als Y", "nicht X, sondern Y", "not X but rather Y", "less about
X, more about Y" — gehaeuft statt konkreter Eigenschaftsnennung.

Signal-DoD (#64): je 3 Positiv / 3 Negativ / 2 Grenz-Fixtures;
Einzeltreffer bleibt unmarkiert (advisory-Grenze, Kollisionsdisziplin
#46), Konfidenz 0.5, detect-only — nie im numerischen Slop-Score.
"""

import os
import sys

SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

import structure_metrics as sm  # noqa: E402


# --- Positives: >= 2 Kontrastframes ----------------------------------------

POS1 = ("Der Wandel ist weniger ein Bruch als vielmehr eine Fortsetzung "
        "bewaehrter Muster. Es ist eher eine Neujustierung als eine "
        "Revolution, wie viele Beobachter meinen. Die Bilanz bleibt "
        "trotzdem ambivalent und die Details verdienen Aufmerksamkeit.")

POS2 = ("Es geht nicht um Geschwindigkeit, sondern um Haltung — so die "
        "these des Berichts. Nicht die Werkzeuge, sondern die Kultur "
        "entscheidet ueber den Erfolg, heisst es weiter. Ob das stimmt, "
        "bleibt offen.")

POS3 = ("It is less about tools and more about habits. It is less "
        "about speed than about care. Teams that internalize this tend "
        "to ship steadier, more considered work over multiple quarters.")

# --- Negatives -------------------------------------------------------------

NEG1 = "Er hat mehr Zeit als Geld und mehr Geduld als Verstand."  # konkreter Vergleich
NEG2 = "Das Ergebnis ist eher kurz als lang und bleibt damit untypisch."  # Einzeltreffer
NEG3 = "Nicht der Preis, sondern die Lieferzeit war das Problem."  # konkrete Fakten, 1 Treffer


# --- Boundaries ------------------------------------------------------------

BOUND1 = NEG1 + " Dennoch bleibt der Eindruck eher bleibend als fluechtig."  # 1 Marker -> None
BOUND2 = (NEG3 + " Spaeter hiess es im Rueckblick: Es war weniger ein "
          "Konflikt als vielmehr ein Missverstaendnis zwischen den Teams.")  # 2 Treffer -> fires


class TestComparativeFramingDoD:
    def test_pos1_de_eher_als(self):
        f = sm.comparative_framing(POS1)
        assert f is not None and f["id"] == "ComparativeFraming"
        assert f["confidence"] <= 0.55

    def test_pos2_de_nicht_sondern(self):
        assert sm.comparative_framing(POS2) is not None

    def test_pos3_en_frames(self):
        assert sm.comparative_framing(POS3) is not None

    def test_neg1_concrete_comparison(self):
        assert sm.comparative_framing(NEG1) is None

    def test_neg2_single_marker(self):
        assert sm.comparative_framing(NEG2) is None

    def test_neg3_single_factual_contrast(self):
        assert sm.comparative_framing(NEG3) is None

    def test_boundary1_single_hit_despite_length(self):
        assert sm.comparative_framing(BOUND1) is None

    def test_boundary2_two_hits_fire(self):
        f = sm.comparative_framing(BOUND2)
        assert f is not None

    def test_short_text_none(self):
        assert sm.comparative_framing("Es ist eher gut als schlecht, oder?") is None

    def test_detect_only_never_scored(self):
        # finding carries no numeric score contribution — only advisory fields
        f = sm.comparative_framing(POS1)
        assert set(f.keys()) >= {"id", "confidence", "evidence", "keep_when"}
        assert "score" not in f


class TestIntegration:
    def test_find_structure_findings_includes_comparative(self):
        findings = sm.find_structure_findings(POS2)
        assert any(f["id"] == "ComparativeFraming" for f in findings)

    def test_clean_text_no_comparative_finding(self):
        text = ("Der Bericht nennt drei konkrete Zahlen, nennt Quellen "
                "und beschreibt ein Verfahren mit reproduzierbaren "
                "Schritten. Alle Aussagen sind belegt und nachvollziehbar "
                "dokumentiert, ohne Ausschmueckungen.")
        assert not any(f["id"] == "ComparativeFraming"
                       for f in sm.find_structure_findings(text))
