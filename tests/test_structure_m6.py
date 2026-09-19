"""Issue #76 Rest — M6: Unpassendes „Fazit"-Kapitel ohne Substanz
(hollow_conclusion, detect-only, structure_metrics.py).

Konzept aus docs/de-coverage.md M6 (NEU klein): Ein Fazit-/Zusammenfassungs-
Heading, dem ein substanzloser Mini-Körper folgt — Schließzwang ohne
Ergebnis. Sprachagnostisch DE+EN (Heading-Stichworte).

Signal-DoD: je 3 Positiv / 3 Negativ / 2 Grenz-Fixtures; Konfidenz 0.5,
detect-only, nie Score-wirksam.
"""

import os
import sys

SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

import structure_metrics as sm  # noqa: E402


# --- M6: Unpassendes Fazit-Kapitel ----------------------------------------

INTRO_TEXT = (
    "## Grundlagen\n\nDie Widget-Engine besteht aus drei Bausteinen: "
    "Parser, Cache und Renderer. Der Parser liest Konfigurationsdateien "
    "ein, der Cache hält Ergebnisse vor, und der Renderer erzeugt daraus "
    "die sichtbare Ausgabe. Ein Konfigurationsbeispiel verdeutlicht das "
    "Zusammenspiel der Bausteine im Betrieb.\n\n"
)

M6_POS1 = INTRO_TEXT + (
    "## Fazit\n\nZusammengefasst lässt sich sagen, dass das Fazit "
    "zusammenfasst."
)

M6_POS2 = INTRO_TEXT + "## Zusammenfassung\n\nDie Punkte wurden gezeigt."

M6_POS3 = (
    "## Analysis\n\nThe pipeline consists of three stages that were "
    "described above in detail, including throughput measurements for "
    "each stage.\n\n"
    "## Conclusion\n\nIn conclusion, this concludes the conclusion."
)

M6_NEG1 = INTRO_TEXT + (
    "## Fazit\n\nDer Parser ist mit 1,2 ms der Flaschenhals; nach dem "
    "Cache-Umbau sank die Renderzeit von 40 ms auf 12 ms, sodass die "
    "Engine jetzt Echtzeit-Anforderungen erfüllt. Offen bleibt die "
    "Speicheranforderung des Caches bei sehr großen Konfigurationen."
)

M6_NEG2 = INTRO_TEXT + "## Fazit\n\nSiehe Abschnitt Grundlagen."

M6_NEG3 = INTRO_TEXT + (
    "## Ausblick\n\nNächster Schritt ist die Portierung des Renderers "
    "auf WebGPU; der Prototyp erreicht bereits 240 fps bei 100k "
    "Punkten. Danach steht die Integration in die Build-Pipeline an."
)

M6_BOUND1 = INTRO_TEXT + (
    "## Fazit\n\nZusammengefasst behandelt der Text die drei Bausteine "
    "der Widget-Engine, nennt deren Zusammenspiel und betont die Rolle "
    "des Caches für die Gesamtperformance der Engine beim Rendern."
)  # 24 Woerter, reine Recap-Pronomina, keine Eigenangabe -> kein Fire (Grenzbereich)

M6_BOUND2 = (
    "Kurzer Text ohne Struktur. ## Fazit\n\nKurz gesagt."
)  # Dokument zu klein (kein Substanz-Minimum vor dem Fazit) -> None


class TestM6HollowConclusion:
    def test_pos1_generic_recap_sentence(self):
        f = sm.hollow_conclusion(M6_POS1)
        assert f is not None and f["id"] == "HollowConclusion"
        assert f["confidence"] <= 0.55
        assert "keep_when" in f

    def test_pos2_minimal_body(self):
        assert sm.hollow_conclusion(M6_POS2) is not None

    def test_pos3_english(self):
        assert sm.hollow_conclusion(M6_POS3) is not None

    def test_neg1_substantive_conclusion(self):
        assert sm.hollow_conclusion(M6_NEG1) is None

    def test_neg2_pointer_conclusion(self):
        # "Siehe Abschnitt Grundlagen." ist kurz, aber ein konkreter
        # Verweis — kein generisches Schließritual. Grenzfall: wir
        # entscheiden bewusst als Negativ (kein Signal).
        assert sm.hollow_conclusion(M6_NEG2) is None

    def test_neg3_substantive_outlook(self):
        assert sm.hollow_conclusion(M6_NEG3) is None

    def test_boundary1_recap_only_but_longer(self):
        assert sm.hollow_conclusion(M6_BOUND1) is None

    def test_boundary2_tiny_document(self):
        assert sm.hollow_conclusion(M6_BOUND2) is None


class TestM6Wiring:
    def test_find_structure_findings_includes_m6(self):
        findings = sm.find_structure_findings(M6_POS1)
        ids = {f["id"] for f in findings}
        assert "HollowConclusion" in ids
        for f in findings:
            assert f["confidence"] <= 0.55
            assert "keep_when" in f
