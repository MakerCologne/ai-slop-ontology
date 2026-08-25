"""DE-Katalog Teil 2 (issue #76): zweite Welle der DE-Phrase-Layer.

12 neue de_*-Kategorien aus docs/de-coverage.md (30 „DE-Variante nötig"-
Prioritäten) — je Kategorie gilt die Signal-DoD (3 Positiv-/3 Negativ-/
2 Grenz-Fixtures, FP-Erwartung dokumentiert). Belegpflicht je Phrase
(RI-1/RI-2 aus Review Batch I: Wikipedia-Projektseite MIT Namespace-
Präfix oder own:-Beleg; ≥2 Belege als dokumentiertes FU offen).
Kollisionsdisziplin (#46): keine Dopplung mit multilingual.german,
bestehenden EN-Kategorien oder anderen de_*-Kategorien (auch nicht
substring-überlappend innerhalb des de_*-Layers).
"""

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from classifier import SlopClassifier  # noqa: E402

ONTOLOGY = os.path.join(ROOT, "ontology.json")
WIKI_SOURCE = ("https://de.wikipedia.org/wiki/"
               "Wikipedia:Anzeichen_f%C3%BCr_KI-generierte_Inhalte")

DE2_CATEGORIES = {
    "de_transitions": "M4 mechanische Konjunktionen",
    "de_recap": "M5 Abschnitts-Zusammenfassungen",
    "de_superlativ": "M2 Werbesprache/Superlative",
    "de_symbolik": "M1 Symbolik-Betonung",
    "de_vague_authority": "M11 vage Autoritaet (Ergaenzung zu #77)",
    "de_participle": "M10 Partizip-I-Anhaengsel",
    "de_binary_contrast": "M8 Parallelkonstruktionen",
    "de_false_range": "M12 Schein-Reichweite (von ... bis)",
    "de_opening": "M36/M37 Universal-Eroeffnung",
    "de_closing": "M38/M62 aspirativer Schluss",
    "de_hedging": "M41/M53 Fehlkalibrierte Gewissheit/Lueckenspekulation",
    "de_announcement_cleft": "M67 Ankuedigungs-Spaltsatz",
}

# Natuerliche deutsche Saetze (handgeschrieben, keine Marker) — Negativ-Pool.
DE_CLEAN = [
    ("Der Ausschuss hat die Zahlen geprüft und festgestellt, dass weitere "
     "Untersuchungen nötig sind, bevor man entscheiden kann."),
    ("Nach dem Sturm war der Dachstuhl schwer beschädigt; die Feuerwehr "
     "sicherte das Gebäude, bis der Handwerker kam."),
    ("Meine Tante kocht am Sonntag immer Kartoffelsalat, auch wenn niemand "
     "besondere Termine dafür angemeldet hat."),
    ("Die Bahn streikt seit Montag, deshalb fährt mein Kollege mit dem "
     "Fahrrad, obwohl der Weg hügelig ist."),
    ("Er legte den Brief auf den Küchentisch und wartete, bis seine "
     "Tochter aus der Schule zurückkam."),
    ("Im Winter lassen wir das Wasser abgestellt, damit das Rohr nicht "
     "einfriert, und kontrollieren das Ventil regelmäßig."),
]

# --- Fixtures je Kategorie: 3 positiv / 3 negativ / 2 grenz ---------------
# Positiv: natürlicher DE-Rahmen + >= 2 Phrasen der Kategorie.
# Negativ: DE_CLEAN ohne Kategorie-Treffer (Kategorie nie in phrase_report).
# Grenze 1: genau EINE Kategorie-Phrase -> advisory (phrase_report), aber
#           KEIN Signal-Match (Cluster-Logik braucht >= 2 Phrase-Hits).
#           FP-Erwartung: Einzeltreffer toleriert, nie score-dominant.
# Grenze 2: Phrase in legitimen Kontext (z. B. wörtlich berichtete Rede
#           oder Fachtext) -> gleiche advisory-Behandlung.
FIXTURES = {
    "de_transitions": {
        "pos": [
            DE_CLEAN[0] + " Darüber hinaus ferner gilt der Bericht als unvollständig.",
            DE_CLEAN[1] + " Zusätzlich außerdem wurden Fenster und Türen geprüft.",
            DE_CLEAN[3] + " Andererseits zusätzlich fährt die Nachbarin mit dem Bus.",
        ],
        "neg": DE_CLEAN[:3],
        "boundary": [
            DE_CLEAN[0] + " Darüber hinaus bleiben drei Fragen offen.",
            DE_CLEAN[4] + " Außerdem stand die Milch noch auf dem Herd.",
        ],
    },
    "de_recap": {
        "pos": [
            DE_CLEAN[0] + " Zusammenfassend abschließend bleibt der Befund offen.",
            DE_CLEAN[1] + " Insgesamt zusammenfassend war der Schaden groß.",
            DE_CLEAN[3] + " Abschließend insgesamt: Das Fazit lautet Streik.",
        ],
        "neg": DE_CLEAN[3:6],
        "boundary": [
            DE_CLEAN[2] + " Insgesamt waren es drei Teller.",
            DE_CLEAN[5] + " Abschließend wies er noch auf das Ventil hin.",
        ],
    },
    "de_superlativ": {
        "pos": [
            DE_CLEAN[0] + " Die Region hat eine reiche Geschichte; atemberaubend ist die Küste.",
            DE_CLEAN[2] + " Der Kuchen war atemberaubend und unbedingt zu besuchen? Nein: ein bleibendes Vermächtnis.",
            DE_CLEAN[4] + " Eine reiche Geschichte und unvergleichliche Küstenabschnitte zeichnen den Ort aus.",
        ],
        "neg": DE_CLEAN[:3],
        "boundary": [
            DE_CLEAN[1] + " Der Ausblick auf das Tal war atemberaubend.",
            DE_CLEAN[4] + " Seine Großmutter hinterließ ein bleibendes Vermächtnis: eine Standuhr.",
        ],
    },
    "de_symbolik": {
        "pos": [
            DE_CLEAN[0] + " Der Bericht steht als Zeugnis und unterstreicht seine Bedeutung.",
            DE_CLEAN[1] + " Das Dorf ist tief verwurzelt und hinterlässt bleibenden Eindruck.",
            DE_CLEAN[3] + " Der Streik spielt eine bedeutende Rolle und fasziniert weiterhin.",
        ],
        "neg": DE_CLEAN[3:6],
        "boundary": [
            DE_CLEAN[0] + " Das Protokoll unterstreicht seine Bedeutung für die Statistik.",
            DE_CLEAN[5] + " Die Familie ist seit Generationen tief verwurzelt.",
        ],
    },
    "de_vague_authority": {
        "pos": [
            DE_CLEAN[0] + " Branchenberichte zeigen: Einige Kritiker argumentieren anders.",
            DE_CLEAN[1] + " Beobachter haben zitiert, Wissenschaftler sind sich einig, dass der Giebel instabil ist.",
            DE_CLEAN[3] + " Zahlreiche Studien belegen, was Experten betonen.",
        ],
        "neg": DE_CLEAN[:3],
        "boundary": [
            DE_CLEAN[0] + " Einige Kritiker argumentieren, der Bericht sei lückenhaft.",
            DE_CLEAN[4] + " Nachbarn zitierten den Brief auswendig.",
        ],
    },
    "de_participle": {
        "pos": [
            DE_CLEAN[0] + " Der Bericht, gewährleistend und hervorhebend, blieb liegen.",
            DE_CLEAN[1] + " Das Team, betonend und widerspiegelnd, arbeitete weiter.",
            DE_CLEAN[5] + " Der Handgriff, unterstreichend und sicherstellend, gelang.",
        ],
        "neg": DE_CLEAN[3:6],
        "boundary": [
            DE_CLEAN[0] + " Die Klausel, sicherstellend, dass nichts verrutscht, gilt seit 2019.",
            DE_CLEAN[5] + " Ein Schild, hervorhebend, wo das Ventil sitzt, hing an der Wand.",
        ],
    },
    "de_binary_contrast": {
        "pos": [
            DE_CLEAN[0] + " Es geht nicht nur um Zahlen; nicht zuletzt zählt auch Frist.",
            DE_CLEAN[2] + " Es geht nicht nur um Salat; nicht zuletzt kommt Wurst dazu.",
            DE_CLEAN[4] + " Es geht nicht nur um Briefe; nicht zuletzt liest sie mit.",
        ],
        "neg": DE_CLEAN[:3],
        "boundary": [
            DE_CLEAN[0] + " Es geht nicht nur um die Zahlen.",
            DE_CLEAN[3] + " Nicht zuletzt wegen des Regens blieb er zu Hause.",
        ],
    },
    "de_false_range": {
        "pos": [
            DE_CLEAN[0] + " Die Vorschläge reichen von traditionell bis modern und von klassisch bis kühn.",
            DE_CLEAN[2] + " Die Preise reichen von günstig bis exquisit und von früh bis spät gereift.",
            DE_CLEAN[4] + " Die Häuser reichen von klassisch bis kühn und von traditionell bis schlicht.",
        ],
        "neg": DE_CLEAN[3:6],
        "boundary": [
            DE_CLEAN[2] + " Die Preise reichen von günstig bis knapp zehn Euro.",
            DE_CLEAN[4] + " Die Jahrgänge reichen von früh bis spät in die Neunziger.",
        ],
    },
    "de_opening": {
        "pos": [
            "Heutzutage mehr denn je ist das Thema präsent. " + DE_CLEAN[0],
            "In der heutigen Zeit, in einer Welt, in der alles schneller geht, "
            "zahlen Firmen Beiträge. " + DE_CLEAN[1],
            "Die Welt wie wir sie kennen ändert sich, heutzutage kontrolliert "
            "man Ventile. " + DE_CLEAN[5],
        ],
        "neg": DE_CLEAN[:3],
        "boundary": [
            "Heutzutage fährt die Bahn pünktlicher als früher. " + DE_CLEAN[3],
            DE_CLEAN[5] + " Das Ventil ist mehr denn je eine Seltenheit.",
        ],
    },
    "de_closing": {
        "pos": [
            DE_CLEAN[0] + " Trotz dieser Erfolge steht der Prozess vor Herausforderungen.",
            DE_CLEAN[1] + " Eines ist sicher: Die Zukunft sieht nass aus.",
            DE_CLEAN[3] + " Grenzenlose Möglichkeiten, eines ist sicher: Fahrrad.",
        ],
        "neg": DE_CLEAN[:3],
        "boundary": [
            DE_CLEAN[1] + " Trotz dieser Erfolge blieb das Dach undicht.",
            DE_CLEAN[4] + " Eines ist sicher: der Herd war aus.",
        ],
    },
    "de_hedging": {
        "pos": [
            DE_CLEAN[0] + " Man könnte argumentieren, dass mehr folgt. Es ist denkbar, dass Klagen kommen.",
            DE_CLEAN[3] + " In gewisser Weise, möglicherweise, ist der Streik auch ein Signal.",
            DE_CLEAN[5] + " Basierend auf verfügbaren Informationen, möglicherweise, friert das Rohr doch.",
        ],
        "neg": DE_CLEAN[3:6],
        "boundary": [
            DE_CLEAN[0] + " In gewisser Weise ist der Bericht ein Fortschritt.",
            DE_CLEAN[4] + " Es ist denkbar, dass die Tochter früher kommt.",
        ],
    },
    "de_announcement_cleft": {
        "pos": [
            DE_CLEAN[0] + " Was mich überraschte: Was viele nicht wissen, steht in Anlage B.",
            DE_CLEAN[1] + " Interessant zu beobachten ist, was dabei auffällt: Riss im Giebel.",
            DE_CLEAN[4] + " Bemerkenswert ist, was oft übersehen wird: der Tisch.",
        ],
        "neg": DE_CLEAN[:3],
        "boundary": [
            DE_CLEAN[3] + " Was mich überraschte, war die Pünktlichkeit.",
            DE_CLEAN[5] + " Bemerkenswert ist die Regelmäßigkeit der Kontrolle.",
        ],
    },
}


def _ontology():
    with open(ONTOLOGY, encoding="utf-8") as f:
        return json.load(f)


def _categories(o):
    return o["signals"]["text"]["phrases"]["categories"]


def _clean_items():
    with open(os.path.join(ROOT, "eval", "corpus.jsonl"), encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()
                and json.loads(l).get("label") == "clean"]


class Part2Schema(unittest.TestCase):
    def test_twelve_new_categories_exist(self):
        cats = _categories(_ontology())
        for cat, concept in DE2_CATEGORIES.items():
            self.assertIn(cat, cats, cat)
            self.assertGreaterEqual(len(cats[cat]["items"]), 5, cat)
            self.assertLessEqual(cats[cat]["confidence"], 0.65, cat)
            self.assertIn(concept.split()[0], cats[cat].get("description", ""))

    def test_every_phrase_has_evidence_with_real_source(self):
        cats = _categories(_ontology())
        for cat in DE2_CATEGORIES:
            evidence = cats[cat].get("evidence", {})
            for phrase in cats[cat]["items"]:
                self.assertIn(phrase, evidence, f"{cat}:{phrase}")
                for src in evidence[phrase]:
                    self.assertTrue(
                        src["source"] == WIKI_SOURCE
                        or src["source"].startswith("own:"),
                        f"{cat}:{phrase}: {src['source']}")

    def test_wikipedia_source_url_has_namespace_prefix(self):
        cats = _categories(_ontology())
        for cat in DE2_CATEGORIES:
            for src in (s for ev in cats[cat]["evidence"].values()
                        for s in ev):
                if src["source"] != WIKI_SOURCE:
                    continue
                self.assertIn("/wiki/Wikipedia:Anzeichen", src["source"],
                              "Projektseiten-URL braucht Namespace-Präfix")


class Part2Collisions(unittest.TestCase):
    def test_no_collision_with_german_buzzwords_or_other_categories(self):
        o = _ontology()
        cats = _categories(o)
        existing = {w.lower() for w in
                    o["signals"]["multilingual"]["german"]["buzzwords"]}
        for cat, data in cats.items():
            if cat in DE2_CATEGORIES:
                continue
            existing |= {p.lower() for p in data["items"]}
        for cat in DE2_CATEGORIES:
            for phrase in cats[cat]["items"]:
                self.assertNotIn(phrase.lower(), existing,
                                 f"Kollision: {cat}:{phrase}")

    def test_de_layer_no_pairwise_substring_overlap(self):
        cats = _categories(_ontology())
        de_phrases = []
        for cat, data in cats.items():
            if cat.startswith("de_"):
                de_phrases += [(cat, p.lower()) for p in data["items"]]
        for i, (c1, p1) in enumerate(de_phrases):
            for c2, p2 in de_phrases[i + 1:]:
                if c1 == c2:
                    continue
                self.assertNotIn(p1, p2, f"Teilstring-Kollision {c1}/{c2}")
                self.assertNotIn(p2, p1, f"Teilstring-Kollision {c2}/{c1}")


class Part2Detection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clf = SlopClassifier(ONTOLOGY)

    def test_classifier_picks_up_new_categories(self):
        text = ("Heutzutage, in der heutigen Zeit, ist vieles atemberaubend. "
                "Darüber hinaus ferner zeigen Branchenberichte, dass "
                "zusammenfassend Grenzenlose Möglichkeiten entstehen, was "
                "viele nicht wissen: Das Fazit lautet Erfolg. Der Bericht "
                "steht als Zeugnis, gewährleistend und hervorhebend, was "
                "oft übersehen wird: Es geht nicht nur um Zahlen, sondern "
                "auch um Pflicht, von traditionell bis modern, in gewisser "
                "Weise denkbar.")
        hit_cats = set(self.clf.classify_text(text).phrase_report)
        for cat in DE2_CATEGORIES:
            self.assertIn(cat, hit_cats, f"{cat} fehlt: {hit_cats}")

    def test_english_clean_corpus_never_hits_new_layer(self):
        for item in _clean_items():
            if item.get("lang", "en") != "en":
                continue
            report = self.clf.classify_text(item["text"]).phrase_report
            self.assertFalse(set(report) & set(DE2_CATEGORIES),
                             f"{item['id']}: {report}")


class Part2SignalDoD(unittest.TestCase):
    """3 Positiv- / 3 Negativ- / 2 Grenz-Fixtures je Kategorie (SIGNAL-DOD)."""

    @classmethod
    def setUpClass(cls):
        cls.clf = SlopClassifier(ONTOLOGY)

    def _report(self, text):
        return self.clf.classify_text(text)

    def _hits(self, text, cat):
        return self._report(text).phrase_report.get(cat, [])

    def test_three_positives_fire_per_category(self):
        for cat, fx in FIXTURES.items():
            for text in fx["pos"]:
                self.assertTrue(self._hits(text, cat),
                                f"{cat}: Positiv-Fixture feuert nicht")

    def test_three_negatives_stay_silent_per_category(self):
        for cat, fx in FIXTURES.items():
            for text in fx["neg"]:
                self.assertEqual(self._hits(text, cat), [],
                                 f"{cat}: Negativ-Fixture feuert: {text}")

    def test_two_boundaries_advisory_only(self):
        # FP-Erwartung: Einzeltreffer erscheint im phrase_report (advisory),
        # erzeugt aber KEIN Signal (Cluster-Logik >= 2 Phrase-Hits gesamt).
        for cat, fx in FIXTURES.items():
            for text in fx["boundary"]:
                res = self._report(text)
                total_hits = sum(len(v) for v in res.phrase_report.values())
                if self._hits(text, cat):
                    self.assertLess(total_hits, 2,
                                    f"{cat}: Grenz-Fixture eskaliert "
                                    f"unerwartet: {res.phrase_report}")
                    self.assertNotIn(
                        "PhrasePattern",
                        [s.signal_id for s in res.signals_detected],
                        f"{cat}: Grenz-Fixture darf kein Signal sein")


if __name__ == "__main__":
    unittest.main()
