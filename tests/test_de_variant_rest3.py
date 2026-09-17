"""#77 DE-Variante-Rest Welle 5 (Idle-Burner 13.09.): fuenfte DE-Phrase-Welle.

3 weitere de_*-Kategorien aus docs/de-coverage.md Offen-Liste:
M7 Dichotom-Schluss + Lob->Herausforderung->Ausblick-Schablone,
M26 Zitat-/Quellenfabrikation, M30 Stilwechsel zwischen Absaetzen —
je Kategorie Signal-DoD (3/3/2-Fixtures, FP-Erwartung dokumentiert),
Belegpflicht je Phrase (RI-1/RI-2: Wikipedia-Projektseite MIT
Namespace-Praefix + own:-Zweibeleg de-ev-23..25).
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
    "de_dichotomy_close": "M7",
    "de_quote_fabrication": "M26",
    "de_register_shift": "M30",
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
    "de_dichotomy_close": {
        "pos": [
            "Die wahre frage lautet: Wer zahlt die Erneuerung? Die gute Nachricht ist, der Rücklage wächst. " + DE_CLEAN[0],
            DE_CLEAN[1] + " Die schlechte Nachricht ist: Der Zeitplan bleibt eng. Die Herausforderung besteht darin, Betrieb und Umbau zu verzahnen.",
            DE_CLEAN[5] + " Die Lösung liegt darin, Abschnitte einzeln zu tauschen. Der erste Schritt besteht darin, den Zustandsbericht zu beauftragen.",
        ],
        "neg": DE_CLEAN[:3],
        "boundary": [
            DE_CLEAN[0] + " Die wahre frage lautet: reicht die Rücklage?",
            DE_CLEAN[4] + " Die gute Nachricht ist, dass der Brief freundlich ausfiel.",
        ],
    },
    "de_quote_fabrication": {
        "pos": [
            "Wie ein Experte einmal sagte: Netze altern still. Ein bekannter Journalist schrieb einst, dass niemand über Rohre spricht. " + DE_CLEAN[0],
            DE_CLEAN[1] + " Wie ein weiser Mann einst sagte — man plant am besten im Trockenen. Ein Insider verriet kürzlich, dass die Ausschreibung vorbereitet liege.",
            DE_CLEAN[3] + " Ein Branchenkenner erklärte, die Margen lägen beim Service. In einem Gespräch gestand ein Betriebsleiter den Zeitdruck.",
        ],
        "neg": DE_CLEAN[:3],
        "boundary": [
            DE_CLEAN[2] + " Wie ein Experte einmal sagte, schmeckt der Salat besser mit Speck.",
            DE_CLEAN[5] + " Ein Branchenkenner erklärte, dass Ventile jährlich zu prüfen sind.",
        ],
    },
    "de_register_shift": {
        "pos": [
            "Der Regelbetrieb folgt etablierten Prüfintervallen. Ganz praktisch gedacht heißt das: alle zwei Jahre Kamera. Anders formuliert — man sieht erst, was man filmt. " + DE_CLEAN[0],
            DE_CLEAN[1] + " Auf den Punkt gebracht: Sichtprüfung ersetzt keine Befahrung. Umschalten wir den Blickwinkel auf die Kosten.",
            DE_CLEAN[5] + " Aus einem anderen Blickwinkel ist jede Inspektion eine Investition. Im Klartext: Wer misst, spart Sanierung.",
        ],
        "neg": DE_CLEAN[:3],
        "boundary": [
            DE_CLEAN[2] + " Anders formuliert schmeckt der Salat auch kalt.",
            DE_CLEAN[4] + " Im Klartext: Der Brief blieb liegen.",
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


class RestDetection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clf = SlopClassifier(ONTOLOGY)

    def test_classifier_picks_up_new_categories(self):
        text = ("Die wahre frage lautet: Wer zahlt das? Die gute Nachricht "
                "ist, der Rücklage wächst. Wie ein Experte einmal sagte: "
                "Netze altern still, und ein Branchenkenner erklärte, die "
                "Margen lägen beim Service. Ganz praktisch gedacht heißt "
                "das: alle zwei Jahre Kamera. Anders formuliert sieht man "
                "erst, was man filmt.")
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
        two = ("Die gute Nachricht ist, dass die Frist hält. Die wahre "
               "frage lautet nur, wer sie kontrolliert.")
        one = "Die wahre frage lautet nur, wer sie kontrolliert. " + DE_CLEAN[0]
        r_two = self.clf.classify_text(two).phrase_report.get(
            "de_dichotomy_close", [])
        r_one = self.clf.classify_text(one).phrase_report.get(
            "de_dichotomy_close", [])
        self.assertEqual(len(r_two), 2, r_two)
        self.assertEqual(len(r_one), 1, r_one)


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
