"""Tests for src/de_ideology.py — detect-only DE/EN-Rhetorik-Layer (#92).

Signal-DoD je Pattern: 3 slop-Fixtures, 3 clean-Fixtures, 2 Edge-Cases
(Promotion nach #98-Korpus, FP=0-Pflicht auf Hard-Negatives).

Vertrag: findings sind advisory, niemals score-wirksam; Detektor bewertet
Strategieform, nicht Parteizugehörigkeit (ADR-0008/0006).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from de_ideology import DeIdeologyClassifier  # noqa: E402

CLF = DeIdeologyClassifier()


def fired(text, pid):
    return any(f.pattern_id == pid for f in CLF.classify_text(text))


# ---------------------------------------------------------------------------
# Fixtures je Pattern: 3 slop / 3 clean / 2 edge
# ---------------------------------------------------------------------------

FIXTURES = {
    # --- RitualFirewall ------------------------------------------------
    "RitualFirewall": {
        "slop": [
            "Die Brandmauer halten — egal was kommt. Darum geht es jetzt.",
            "Unsere einzige Aufgabe ist es, die Brandmauer zu verteidigen, gegen jeden.",
            "Keine Kooperation, keine Gespräche: die Brandmauer halten, fertig.",
        ],
        "clean": [
            "Der Untersuchungsausschuss prüft die Vorgänge im Ministerium.",
            "Nach der Wahl wird eine Minderheitsregierung angestrebt.",
            "Die Koordinaten der Debatte verschieben sich, sagt die Analyse.",
        ],
        "edge": [
            # Satire (klar markiert) → kein Fund
            "Satire: Selbst die Brandmauer hat inzwischen einen Wartungsblog.",
            # Konkretes Policy-Instrument im selben Satz → keep_when
            "Die Brandmauer halten wir über ein Verbotsverfahren, nicht über Rhetorik.",
        ],
    },
    # --- MartyrCartel --------------------------------------------------
    "MartyrCartel": {
        "slop": [
            "Die Altparteien und ihre Systempresse werden das wieder vertuschen, wie immer.",
            "Die Lügenpresse berichtet nicht, was wirklich passiert.",
            "Das Kartell der alten Parteien verhindert jede echte Alternative.",
        ],
        "clean": [
            "Das Protokoll der Sitzung wurde heute veröffentlicht.",
            "Az. 4 C 12/23: Gericht entschied über die Klage.",
            "Nach dem Urteil des Landgerichts ist der Streit beigelegt.",
        ],
        "edge": [
            # Einzelvorgang mit Beleg → keep_when
            "Die Systempresse-debatte bezieht sich auf Beschluss 21/3 des Stadtrats.",
            # wörtliche Erwähnung in Analyse (mit Protokollbezug)
            "Im Protokoll wird der Begriff Lügenpresse als Zitat geführt.",
        ],
    },
    # --- CollectiveOther -----------------------------------------------
    "CollectiveOther": {
        "slop": [
            "Die Migranten sind nun mal so, das weiß man doch.",
            "Die Ausländer sind alle gleich, bringt nichts, das zu leugnen.",
            "Those migrants are simply like that, everyone knows it.",
        ],
        "clean": [
            "2023 lag die Zahl der Erstanträge bei 329.000 (Quelle: BAMF).",
            "Die Studie von 2024 zeigt differenzierte Integrationsverläufe.",
            "42 % der Befragten gaben an, Sprachkurse zu besuchen.",
        ],
        "edge": [
            # Statistik im selben Satz → keep_when unterdrückt
            "Die Migranten sind laut BAMF-Statistik 2024 zu 61 % erwerbstätig.",
            # Einzelfall statt Kollektiv → kein Trigger
            "Ein einzelner Tatverdächtiger wurde festgenommen.",
        ],
    },
    # --- ReplacementKicker ----------------------------------------------
    "ReplacementKicker": {
        "slop": [
            "Und am Ende ist das Land, das wir kannten, einfach nicht mehr da.",
            "Der Bevölkerungsaustausch schreitet weiter voran.",
            "Sie nennen es Great Replacement — und leugnen es zugleich.",
        ],
        "clean": [
            "Die Geburtenrate sank 2023 auf 1,35 (Destatis).",
            "Der Wanderungssaldo betrug 2022 rund +1,1 Mio. (Quelle: Eurostat).",
            "Demografie-Modelle rechnen mit mehreren Szenarien bis 2040.",
        ],
        "edge": [
            # Demografie mit Quelle → keep_when
            "Kritiker sprechen von Bevölkerungsaustausch; die Daten (Destatis 2023) zeigen Wanderungsbewegungen.",
            # wissenschaftliche Erwähnung mit Jahreszahl
            "Der Begriff Great Replacement taucht 2019 erstmals in Manifesten auf.",
        ],
    },
    # --- EthnopluralistRebrand -------------------------------------------
    "EthnopluralistRebrand": {
        "slop": [
            "Echte Vielfalt lebt von der Trennung — jeder bleibe unter seinen eigenen Traditionen.",
            "Das Recht auf Differenz verlangt getrennte Räume.",
            "Ethnopluralismus ist keine Ideologie, nur Respekt vor Verschiedenheit.",
        ],
        "clean": [
            "Die ethnografische Studie beschreibt Heiratspraktiken in drei Dörfern.",
            "Die völkerkundliche Sammlung wurde neu kuratiert.",
            "Forschung zu kultureller Vielfalt braucht Feldarbeit vor Ort.",
        ],
        "edge": [
            # ethnografischer Kontext → keep_when
            "Ethnopluralismus als Begriff stammt aus der Forschung zur Nouvelle Droite.",
            # Beschreibung ohne Segregationsforderung
            "Die Trennung der Kulturen beschreibt die Ethnografie als Beobachtung, nicht als Forderung.",
        ],
    },
    # --- PurityBan -------------------------------------------------------
    "PurityBan": {
        "slop": [
            "AI is theft. Pass it on.",
            "Wir brauchen ein Totalverbot dieser Technologie, sofort.",
            "Ban all AI — alles andere ist Verrat.",
        ],
        "clean": [
            "Das Urheberrechtsverfahren zu Trainingsdaten beginnt im Mai.",
            "Der dokumentierte Scraping-Fall ist vor Gericht.",
            "Die Klage betrifft konkrete Werke mit Aktenzeichen.",
        ],
        "edge": [
            # konkreter Rechtsfall → keep_when
            "AI is theft? Das Verfahren dazu wird zeigen, welche Werke betroffen sind.",
            # Differenzierung statt Totalverbot → kein Trigger
            "Für spezifische Anwendungen braucht es Regeln, nicht Pauschalverbote.",
        ],
    },
    # --- VibeScapegoat ---------------------------------------------------
    "VibeScapegoat": {
        "slop": [
            "Service down again? Vibe-coded slop devs at work, as always.",
            "Schon wieder Ausfall — vibe coding devs, keine Frage.",
            "Vibe-coded devs bauen einfach nichts Stabiles.",
        ],
        "clean": [
            "Das Postmortem zeigt einen Konfigurationsfehler als Ursache.",
            "Der Commit fixt die Regression im Retry-Pfad.",
            "Laut Incident-Report war ein fehlerhafter Diff verantwortlich.",
        ],
        "edge": [
            # Diff/Postmortem im Text → keep_when
            "Vibe-coded slop devs? Das Postmortem belegt einen Load-Balancer-Bug.",
            # Einzelner belegter Fall statt Pauschale
            "Der eine Ausfall hatte einen dokumentierten Commit als Ursache.",
        ],
    },
    # --- SalvationModel --------------------------------------------------
    "SalvationModel": {
        "slop": [
            "Nur noch X kann das Land retten — alle anderen sind Teil des Problems.",
            "Nur diese Partei kann uns noch retten.",
            "Only X can save us now.",
        ],
        "clean": [
            "Wenn der Benchmark erfüllt ist, gilt das Modell als einsatzbereit (Test-Bedingung).",
            "Die Wahlprognose sieht ein Kopf-an-Kopf-Rennen.",
            "Der Einzelclaim ist belegt durch die Evaluationsstudie.",
        ],
        "edge": [
            # Testbedingung → keep_when
            "Nur X kann uns retten, wenn der Test unter definierten Bedingungen bestanden wird.",
            # ironisch markiert
            "Satire: Nur X kann uns retten, steht auch auf dem T-Shirt.",
        ],
    },
    # --- UnfalsifiableTemplate -------------------------------------------
    "UnfalsifiableTemplate": {
        "slop": [
            "Was diese Woche passierte, bestätigt nur, was wir immer gesagt haben.",
            "Genau wie wir es immer gesagt haben — wieder einmal.",
            "This proves what we've been saying all along.",
        ],
        "clean": [
            "Erstmals liegen Daten von 2025 vor, die das Bild verändern.",
            "Zum ersten Mal wurde die Methode unabhängig repliziert.",
            "Der Bericht bringt neue Information zu den Abläufen.",
        ],
        "edge": [
            # neue Information im Text → keep_when
            "Das bestätigt, was wir gesagt haben — und liefert zudem Zahlen vom 03.04.2026.",
            # wörtliches Zitat in Analyse
            "Das Zitat „bestätigt nur, was wir immer gesagt haben“ stammt aus dem Jahr 2021.",
        ],
    },
    # --- EnemyVermin ------------------------------------------------------
    "EnemyVermin": {
        "slop": [
            "Diese Leute sind Ungeziefer und gehören entfernt.",
            "Untermenschen haben in unserem Land nichts zu sagen.",
            "They are vermin, nothing less.",
        ],
        "clean": [
            "In der Satire-Sendung wurde die Rhetorik persifliert.",
            "Die Glosse nimmt die Debatte ironisch auseinander.",
            "Historische Analyse zum Sprachgebrauch von „Ungeziefer“ 1933–45.",
        ],
        "edge": [
            # klar markierte Satire → keep_when
            "Satire: Die Kakerlaken im Rathaus sind leider echte Schaben (ironisch gemeint).",
            # wörtliches Zitat markiert
            "Er nannte sie „Ratten“ — das Zitat steht in Anführungszeichen im Protokoll.",
        ],
    },
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def _test_pattern(pid):
    fx = FIXTURES[pid]
    for t in fx["slop"]:
        assert fired(t, pid), f"{pid} SLOP-Fixture sollte feuern: {t!r}"
    for t in fx["clean"]:
        assert not fired(t, pid), f"{pid} CLEAN-Fixture darf nicht feuern: {t!r}"
    for t in fx["edge"]:
        assert not fired(t, pid), f"{pid} EDGE-Fixture (keep_when) darf nicht feuern: {t!r}"


def test_all_patterns_332():
    for pid in FIXTURES:
        _test_pattern(pid)


def test_detect_only_contract():
    """Findings sind advisory: classifier hat keinen Score-Effekt."""
    assert CLF.score_effect.startswith("none")


def test_named_evidence():
    """Jeder Fund liefert zitiertes Belegstück (named evidence)."""
    f = CLF.classify_text("Die Brandmauer halten — egal was kommt.")
    assert f and all("…" in x.evidence for x in f)


def test_strategy_not_party():
    """Parteinamen allein feuern nicht — Strategieform, nicht Zugehörigkeit."""
    assert not CLF.classify_text("Die SPD hat den Kompromiss mitgetragen.")
    assert not CLF.classify_text("AfD und CDU streiten über Haushaltspositionen.")


def test_empty_text():
    assert CLF.classify_text("") == []
