"""#77 DE-Variante-Rest Welle 6 (Idle-Burner 15.09.): sechste DE-Phrase-Welle.

3 weitere de_*-Kategorien aus docs/de-coverage.md Offen-Liste:
M32 rhetorische Einstiegsfloskeln (disjunkt zu de_authority_floskel),
M56 Aphorismus-Formeln, M72 pseudo-therapeutische Validierung —
je Kategorie Signal-DoD (3/3/2-Fixtures, FP-Erwartung dokumentiert),
Belegpflicht je Phrase (RI-1/RI-2: Wikipedia-Projektseite MIT
Namespace-Praefix + own:-Zweibeleg de-ev-26..28).
Kollisionsdisziplin (#46): keine Dopplung mit multilingual.german,
bestehenden EN-Kategorien oder anderen de_*-Kategorien (auch nicht
substring-ueberlappend).
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
    "de_rhetorical_setup": "M32",
    "de_aphorism": "M56",
    "de_therapeutic_validation": "M72",
}

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
    "de_rhetorical_setup": {
        "pos": [
            "Die entscheidende Frage lautet: Wer trägt den Unterhalt? Was uns wirklich beschäftigt ist die Zuständigkeit. " + DE_CLEAN[0],
            DE_CLEAN[1] + " Im Kern geht es um die Verteilung der Pumpkosten. Das eigentlich spannende ist die Nutzervereinbarung.",
            DE_CLEAN[5] + " Worum es wirklich geht, ist die Grundsatzentscheidung. Am Ende bleibt die Erkenntnis, dass Beete kein Regenkonzept ersetzen.",
        ],
        "neg": DE_CLEAN[:3],
        "boundary": [
            DE_CLEAN[0] + " Die entscheidende Frage lautet am Ende doch immer: Was kostet das?",
            DE_CLEAN[4] + " Im Kern geht es um den alten Briefkopf.",
        ],
    },
    "de_aphorism": {
        "pos": [
            "Denn eines ist klar: Niemand sucht, was er nicht vermisst. Denn eines steht fest — Pech trifft auch Kartenaugen. " + DE_CLEAN[0],
            DE_CLEAN[2] + " Daraus lässt sich eines lernen über alte Pläne. Vielleicht ist es genau das, was einen Hof lebendig hält.",
            DE_CLEAN[3] + " Vielleicht liegt darin die Antwort auf den Wert alter Karten. Und genau darin liegt die Wahrheit.",
        ],
        "neg": DE_CLEAN[:3],
        "boundary": [
            DE_CLEAN[2] + " Denn eines ist klar: Der Salat wird nicht besser.",
            DE_CLEAN[5] + " Daraus lässt sich eines lernen über Frostschäden.",
        ],
    },
    "de_therapeutic_validation": {
        "pos": [
            "Es ist völlig normal, dass die ersten Wochen überfordern. Deine Gefühle sind berechtigt, auch wenn andere schneller wirken. " + DE_CLEAN[0],
            DE_CLEAN[1] + " Sei sanft mit dir selbst — der Stundenplan ist kein Wettrennen. Du bist nicht allein damit.",
            DE_CLEAN[5] + " Gib dir die Zeit, die du brauchst. Und es ist okay, Hilfe anzunehmen, wenn die Klausurphase naht.",
        ],
        "neg": DE_CLEAN[:3],
        "boundary": [
            DE_CLEAN[2] + " Es ist völlig normal, dass der Salat kalt gegessen wird.",
            DE_CLEAN[4] + " Du bist nicht allein damit, samstags Briefe zu sortieren.",
        ],
    },
}


def _ontology():
    with open(ONTOLOGY, encoding="utf-8") as f:
        return json.load(f)


def _categories(o):
    return o["signals"]["text"]["phrases"]["categories"]


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
            for phrase in cats[cat]["items"]:
                wiki = [s["source"] for s in cats[cat]["evidence"][phrase]
                        if s["source"].startswith("https://de.wikipedia.org")]
                for url in wiki:
                    self.assertIn("/wiki/Wikipedia:", url)

    def test_own_evidence_ids_resolve(self):
        cats = _categories(_ontology())
        with open(os.path.join(ROOT, "eval", "de_evidence_texts.jsonl"),
                  encoding="utf-8") as f:
            corpus = {json.loads(l)["id"]: json.loads(l) for l in f if l.strip()}
        for cat in REST_CATEGORIES:
            for phrase in cats[cat]["items"]:
                own = [s for s in cats[cat]["evidence"][phrase]
                       if s["source"] == "own:corpus"]
                self.assertTrue(own, f"{cat}:{phrase}")
                ev_id = "de-ev-" + own[0]["note"].split("(de-ev-")[1].split(")")[0]
                self.assertIn(ev_id, corpus, f"{cat}:{phrase}:{ev_id}")
                self.assertIn(phrase,
                              [x.lower() for x in corpus[ev_id]["phrases"]],
                              f"{cat}:{phrase} fehlt in {ev_id}")

    def test_no_substring_collision_with_other_categories(self):
        cats = _categories(_ontology())
        all_items = [(c, p.lower())
                     for c, v in cats.items() for p in v.get("items", [])]
        for cat in REST_CATEGORIES:
            for phrase in cats[cat]["items"]:
                pl = phrase.lower()
                for other, op in all_items:
                    if other == cat and op == pl:
                        continue
                    self.assertFalse(
                        op in pl or pl in op,
                        f"Kollision {cat}:'{phrase}' vs {other}:'{op}'")

    def test_fixtures_dod(self):
        # Signal-DoD: 3 pos / 3 neg / 2 boundary je Kategorie
        for cat in REST_CATEGORIES:
            self.assertEqual(len(FIXTURES[cat]["pos"]), 3, cat)
            self.assertEqual(len(FIXTURES[cat]["neg"]), 3, cat)
            self.assertEqual(len(FIXTURES[cat]["boundary"]), 2, cat)


class RestDetection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clf = SlopClassifier(ONTOLOGY)

    def test_classifier_picks_up_new_categories(self):
        text = ("Die entscheidende Frage lautet: Wer trägt den Unterhalt? "
                "Was uns wirklich beschäftigt ist die Zuständigkeit. "
                "Denn eines ist klar: Niemand sucht, was er nicht vermisst. "
                "Und genau darin liegt die Wahrheit. Es ist völlig normal, "
                "dass die ersten Wochen überfordern. Deine Gefühle sind "
                "berechtigt.")
        hit_cats = set(self.clf.classify_text(text).phrase_report)
        for cat in REST_CATEGORIES:
            self.assertIn(cat, hit_cats, f"{cat} fehlt: {hit_cats}")

    def test_english_clean_corpus_never_hits_new_layer(self):
        for item in _clean_items():
            if item.get("lang", "en") != "en":
                continue
            with self.subTest(clean=item.get("id", item["text"][:30])):
                self.assertEqual(
                    self.clf.classify_text(item["text"]).phrase_report, {})

    def test_category_boundary_hit_counts(self):
        # Cluster-Logik: Einzeltreffer = 1 Hit (advisory), 2 Treffer = 2 Hits
        two = ("Denn eines ist klar: Der Brunnen blieb trocken. "
               "Denn eines steht fest — Nachbarn graben anders.")
        one = "Denn eines ist klar: Der Brunnen blieb trocken. " + DE_CLEAN[0]
        r_two = self.clf.classify_text(two).phrase_report.get(
            "de_aphorism", [])
        r_one = self.clf.classify_text(one).phrase_report.get(
            "de_aphorism", [])
        self.assertEqual(len(r_two), 2, r_two)
        self.assertEqual(len(r_one), 1, r_one)

    def test_clean_german_never_signals(self):
        # FP-Erwartung: saubere DE-Alltagstexte erzeugen keine >=2-Hit-Cluster
        for i, text in enumerate(DE_CLEAN):
            with self.subTest(clean=i):
                for cat in REST_CATEGORIES:
                    hits = self.clf.classify_text(text).phrase_report.get(cat, [])
                    self.assertLess(len(hits), 2, f"{cat} auf clean: {hits}")


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


def _clean_items():
    with open(os.path.join(ROOT, "eval", "corpus.jsonl"), encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()
                and json.loads(l).get("label") == "clean"]


if __name__ == "__main__":
    unittest.main()
