"""Issue #76 Rest — Strukturmetrik-Rest: M66 Fake-Analyse-Anhang und
M71 Retroaktive Scheinnuance (detect-only, structure_metrics.py).

M67 (Ankündigungs-Spaltsatz) ist bereits als de_announcement_cleft-
Phrase-Kategorie gedeckt (Teil 2) — hier bewusst KEINE Duplikation
(Kollisionsdisziplin #46).

Signal-DoD: je 3 Positiv / 3 Negativ / 2 Grenz-Fixtures; Einzeltreffer
bleiben unmarkiert (advisory-Grenze), Konfidenz 0.5, detect-only.
"""

import os
import sys

SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

import structure_metrics as sm  # noqa: E402


# --- M66: Fake-Analyse-Anhang ---------------------------------------------

M66_POS1 = ("Die neue Richtlinie ist ein Meilenstein, der die Art, wie wir "
            "Dokumente prüfen, verändert. Zugleich ist es ein Schritt, der "
            "die Branche nachhaltig prägt. Alle Beteiligten sprachen von "
            "einem Wendepunkt, der die Spielregeln neu definiert.")

M66_POS2 = ("Es ist eine Entscheidung, die die Art, wie wir arbeiten, "
            "verändert — und ein Signal, das den Wandel unterstreicht. "
            "Manche nennen es eine Zäsur, welche die Zukunft prägt.")

M66_POS3 = ("Der Bericht enthält eine Passage, die die Kernaussage "
            "unterstreicht, und ein Kapitel, das die Debatte verändert. "
            "Beide Elemente wirken analytisch, ohne neue Informationen "
            "zu liefern.")

M66_NEG1 = "Der Zeuge nannte einen Namen, der den Verdächtigen belastet."
M66_NEG2 = ("Wir suchten ein Haus, das Platz für sechs Personen bietet, "
            "und eine Wohnung, die im Erdgeschoss liegt.")
M66_NEG3 = ("Das Gesetz, das 1994 verabschiedet wurde, gilt weiterhin. "
            "Die Verordnung, die es ergänzt, trat 2003 in Kraft.")

M66_BOUND1 = M66_NEG2 + " Nur eine Formulierung, die die Debatte verändert, blieb übrig."
M66_BOUND2 = "Ein einziger Absatz, der die Stimmung unterstreicht, genügte der Redaktion."  # 1 Treffer -> None


class TestM66FakeAnalysisAppendix:
    def test_pos1(self):
        f = sm.fake_analysis_appendix(M66_POS1)
        assert f is not None and f["id"] == "FakeAnalysisAppendix"
        assert f["confidence"] <= 0.55

    def test_pos2(self):
        assert sm.fake_analysis_appendix(M66_POS2) is not None

    def test_pos3(self):
        assert sm.fake_analysis_appendix(M66_POS3) is not None

    def test_neg1_informative_relative_clause(self):
        assert sm.fake_analysis_appendix(M66_NEG1) is None

    def test_neg2_everyday_relative_clauses(self):
        assert sm.fake_analysis_appendix(M66_NEG2) is None

    def test_neg3_factual_relative_clauses(self):
        assert sm.fake_analysis_appendix(M66_NEG3) is None

    def test_boundary1_single_hit_with_filler(self):
        assert sm.fake_analysis_appendix(M66_BOUND1) is None

    def test_boundary2_single_hit(self):
        assert sm.fake_analysis_appendix(M66_BOUND2) is None

    def test_short_text_none(self):
        assert sm.fake_analysis_appendix("Ein Schritt, der alles verändert.") is None


# --- M71: Retroaktive Scheinnuance ----------------------------------------

M71_POS1 = ("Der Umsatz stagnierte. Genauer gesagt: Er stagnierte seit "
            "drei Quartalen. Streng genommen war das keine Stagnation, "
            "sondern ein leichter Rückgang.")

M71_POS2 = ("Das Modell liefert brauchbare Ergebnisse. Um es genauer zu "
            "sagen: brauchbare für einfache Fälle. Präziser formuliert "
            "handelt es sich um eine Heuristik.")

M71_POS3 = ("The results hold for small samples. To be precise, for very "
            "small samples. Strictly speaking, the claim only covers n<10. "
            "More precisely, n<8.")

M71_NEG1 = "Die Ergebnisse sind eindeutig und bedürfen keiner Einschränkung."
M71_NEG2 = ("Genauer als die Vorgängerversion ist die Prognose trotzdem "
            "nicht, das liegt an der Datenlage.")
M71_NEG3 = "Wir präzisieren die Angaben im nächsten Bericht."

M71_BOUND1 = "Der Trend ist stabil. Genauer gesagt, stabil bei niedrigem Niveau."
M71_BOUND2 = "Alles lief planmäßig. Streng genommen war eine Anzeige verspätet."


class TestM71PseudoNuance:
    def test_pos1(self):
        f = sm.pseudo_nuance(M71_POS1)
        assert f is not None and f["id"] == "PseudoNuance"
        assert f["confidence"] <= 0.55

    def test_pos2(self):
        assert sm.pseudo_nuance(M71_POS2) is not None

    def test_pos3(self):
        assert sm.pseudo_nuance(M71_POS3) is not None

    def test_neg1_plain(self):
        assert sm.pseudo_nuance(M71_NEG1) is None

    def test_neg2_comparative_not_marker(self):
        assert sm.pseudo_nuance(M71_NEG2) is None

    def test_neg3_plain_verb(self):
        assert sm.pseudo_nuance(M71_NEG3) is None

    def test_boundary1_single_marker(self):
        assert sm.pseudo_nuance(M71_BOUND1) is None

    def test_boundary2_single_marker(self):
        assert sm.pseudo_nuance(M71_BOUND2) is None


class TestFindingsWiring:
    def test_find_structure_findings_includes_new_signals(self):
        findings = sm.find_structure_findings(M66_POS1 + " " + M71_POS1)
        ids = {f["id"] for f in findings}
        assert "FakeAnalysisAppendix" in ids
        assert "PseudoNuance" in ids
        for f in findings:
            assert f["confidence"] <= 0.55
            assert "keep_when" in f
