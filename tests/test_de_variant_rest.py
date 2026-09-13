"""#77 DE-Variante-Rest (Idle-Burner 13.09.): dritte Welle der DE-Phrase-Layer.

3 neue de_*-Kategorien aus docs/de-coverage.md Offen-Liste
(DE-VARIANTE/NEU-Rest): M18 Chatbot-Restfloskeln, M33 Signposting,
M65 Kopula-Vermeidung — je Kategorie Signal-DoD (3/3/2-Fixtures,
FP-Erwartung dokumentiert), Belegpflicht je Phrase (RI-1/RI-2:
Wikipedia-Projektseite MIT Namespace-Präfix + own:-Zweibeleg,
alle 6 Phrasen je Kategorie mit Belegtext de-ev-17..19 abgedeckt).
Kollisionsdisziplin (#46): keine Dopplung mit multilingual.german,
bestehenden EN-Kategorien oder anderen de_*-Kategorien (auch nicht
substring-überlappend).
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

REST_CATEGORIES = {
    "de_chatbot_leftover": "M18",
    "de_signposting": "M33",
    "de_copula_avoidance": "M65",
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

# 3 positiv / 3 negativ / 2 grenz je Kategorie. Positiv: >= 2 Phrasen.
# Grenze: genau EINE Phrase -> advisory (phrase_report), KEIN Signal-Match
# (Cluster-Logik >= 2 Hits). FP-Erwartung: Einzeltreffer toleriert.
FIXTURES = {
    "de_chatbot_leftover": {
        "pos": [
            DE_CLEAN[0] + " Ich hoffe, das hilft; lassen Sie mich wissen, ob Angaben fehlen.",
            DE_CLEAN[1] + " Gerne helfe ich weiter. Bei weiteren Fragen zögern Sie nicht nachzufragen.",
            DE_CLEAN[3] + " Ich hoffe, das war hilfreich. Lassen Sie mich wissen, was noch offen ist.",
        ],
        "neg": DE_CLEAN[:3],
        "boundary": [
            DE_CLEAN[0] + " Ich hoffe, das hilft dem Ausschuss.",
            DE_CLEAN[4] + " Bei weiteren Fragen ist das Amt zuständig.",
        ],
    },
    "de_signposting": {
        "pos": [
            "In diesem Abschnitt werden wir die Wartung beschreiben. Im folgenden werden wir die Fristen nennen. " + DE_CLEAN[0],
            DE_CLEAN[1] + " Wenden wir uns nun dem Dach. Sehen wir uns genauer an, welche Ziegel fehlen.",
            DE_CLEAN[5] + " Kommen wir nun zum Ventil. Ein genauerer Blick auf die Dichtung lohnt sich.",
        ],
        "neg": DE_CLEAN[:3],
        "boundary": [
            DE_CLEAN[2] + " In diesem Abschnitt werden wir nicht weiter ausholen.",
            DE_CLEAN[3] + " Wenden wir uns nun dem eigentlichen Thema.",
        ],
    },
    "de_copula_avoidance": {
        "pos": [
            "Die Stelle fungiert als Schnittstelle und agiert als Ansprechpartner für Statistik. " + DE_CLEAN[0],
            DE_CLEAN[1] + " Das Register funktioniert als Nachweisstelle und spielt die Rolle von Index und Verzeichnis.",
            DE_CLEAN[4] + " Der Beauftragte nimmt die Rolle einer Meldestelle ein und ist in der Funktion eines Koordinators tätig.",
        ],
        "neg": DE_CLEAN[:3],
        "boundary": [
            DE_CLEAN[0] + " Die Kennzahl fungiert als Frühindikator.",
            DE_CLEAN[5] + " Das Ventil funktioniert als Rücklaufsperre.",
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


class RestSchema(unittest.TestCase):
    def test_three_new_categories_exist(self):
        cats = _categories(_ontology())
        for cat in REST_CATEGORIES:
            self.assertIn(cat, cats, cat)
            self.assertGreaterEqual(len(cats[cat]["items"]), 5, cat)
            self.assertLessEqual(cats[cat]["confidence"], 0.65, cat)
            self.assertIn(REST_CATEGORIES[cat], cats[cat].get("description", ""))

    def test_every_phrase_has_evidence_with_real_source(self):
        cats = _categories(_ontology())
        for cat in REST_CATEGORIES:
            evidence = cats[cat].get("evidence", {})
            for phrase in cats[cat]["items"]:
                self.assertIn(phrase, evidence, f"{cat}:{phrase}")
                sources = [s["source"] for s in evidence[phrase]]
                self.assertTrue(
                    all(s == WIKI_SOURCE or s.startswith("own:") for s in sources),
                    f"{cat}:{phrase}: {sources}")
                # dieser Batch: Voll-Zweibeleg (Wiki + own:corpus)
                self.assertEqual(len(sources), 2, f"{cat}:{phrase}")

    def test_wikipedia_source_url_has_namespace_prefix(self):
        cats = _categories(_ontology())
        for cat in REST_CATEGORIES:
            for src in (s for ev in cats[cat]["evidence"].values() for s in ev):
                if src["source"] != WIKI_SOURCE:
                    continue
                self.assertIn("/wiki/Wikipedia:Anzeichen", src["source"])


class RestCollisions(unittest.TestCase):
    def test_no_collision_with_german_buzzwords_or_other_categories(self):
        o = _ontology()
        cats = _categories(o)
        existing = {w.lower() for w in
                    o["signals"]["multilingual"]["german"]["buzzwords"]}
        for cat, data in cats.items():
            if cat in REST_CATEGORIES:
                continue
            existing |= {p.lower() for p in data["items"]}
        for cat in REST_CATEGORIES:
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


class RestDetection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clf = SlopClassifier(ONTOLOGY)

    def test_classifier_picks_up_new_categories(self):
        text = ("Die Stelle fungiert als Schnittstelle und agiert als "
                "Ansprechpartner. Ich hoffe, das hilft; lassen Sie mich "
                "wissen, ob Angaben fehlen. In diesem Abschnitt werden wir "
                "die Fristen nennen; im folgenden werden wir das Ventil "
                "beschreiben. Gerne helfe ich weiter.")
        hit_cats = set(self.clf.classify_text(text).phrase_report)
        for cat in REST_CATEGORIES:
            self.assertIn(cat, hit_cats, f"{cat} fehlt: {hit_cats}")

    def test_english_clean_corpus_never_hits_new_layer(self):
        for item in _clean_items():
            if item.get("lang", "en") != "en":
                continue
            report = self.clf.classify_text(item["text"]).phrase_report
            self.assertFalse(set(report) & set(REST_CATEGORIES),
                             f"{item['id']}: {report}")


class RestSignalDoD(unittest.TestCase):
    """3 Positiv- / 3 Negativ- / 2 Grenz-Fixtures je Kategorie."""

    @classmethod
    def setUpClass(cls):
        cls.clf = SlopClassifier(ONTOLOGY)

    def _hits(self, text, cat):
        return self.clf.classify_text(text).phrase_report.get(cat, [])

    def test_positives_report_category(self):
        for cat, fx in FIXTURES.items():
            for i, text in enumerate(fx["pos"]):
                self.assertTrue(self._hits(text, cat),
                                f"{cat} pos[{i}] ohne Treffer")

    def test_negatives_never_report_category(self):
        for cat, fx in FIXTURES.items():
            for i, text in enumerate(fx["neg"]):
                self.assertFalse(self._hits(text, cat),
                                 f"{cat} neg[{i}] faelschlich getriggert")

    def test_boundaries_advisory_only_single_hit(self):
        for cat, fx in FIXTURES.items():
            for i, text in enumerate(fx["boundary"]):
                hits = self._hits(text, cat)
                self.assertLessEqual(len(hits), 1,
                                     f"{cat} boundary[{i}] >1 Treffer")


if __name__ == "__main__":
    unittest.main()
