"""DE-KI-Marker-Vokabular (issue #77): de_calque / de_ai_vocab /
de_authority_floskel / de_meta_comment als DE-Layer der Phrase-Datenbank
in ontology.json (SSOT #49). Jede Phrase braucht ≥1 Belegquelle.
Kollisionsdisziplin (#46): keine Dopplung mit signals.multilingual.german
oder bestehenden EN-Kategorien.
"""

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from classifier import SlopClassifier  # noqa: E402

ONTOLOGY = os.path.join(ROOT, "ontology.json")
DE_CATEGORIES = ("de_calque", "de_ai_vocab", "de_authority_floskel",
                 "de_meta_comment")
WIKI_SOURCE = ("https://de.wikipedia.org/wiki/"
               "Anzeichen_f%C3%BCr_KI-generierte_Inhalte")


def _ontology():
    with open(ONTOLOGY, encoding="utf-8") as f:
        return json.load(f)


def _categories(o):
    return o["signals"]["text"]["phrases"]["categories"]


def _clean_items():
    with open(os.path.join(ROOT, "eval", "corpus.jsonl"), encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()
                and json.loads(l).get("label") == "clean"]


class DeVocabSchema(unittest.TestCase):
    def test_four_categories_exist_with_min_items(self):
        cats = _categories(_ontology())
        for cat in DE_CATEGORIES:
            self.assertIn(cat, cats)
            self.assertGreaterEqual(len(cats[cat]["items"]), 5, cat)
            self.assertIn("confidence", cats[cat])
            self.assertLessEqual(cats[cat]["confidence"], 0.65)

    def test_every_phrase_has_evidence_with_source(self):
        cats = _categories(_ontology())
        for cat in DE_CATEGORIES:
            evidence = cats[cat].get("evidence", {})
            for phrase in cats[cat]["items"]:
                self.assertIn(phrase, evidence, f"{cat}:{phrase}")
                sources = evidence[phrase]
                self.assertTrue(sources, f"{cat}:{phrase} ohne Quelle")
                for src in sources:
                    self.assertIn("source", src)
                    self.assertTrue(
                        src["source"].startswith("https://de.wikipedia.org")
                        or src["source"].startswith("own:"),
                        f"{cat}:{phrase}: Quelle weder Wikipedia noch eigener "
                        f"Beleg: {src['source']}")

    def test_evidence_sources_are_real_kinds(self):
        cats = _categories(_ontology())
        wiki_seen = any(
            src["source"].startswith("https://de.wikipedia.org")
            for cat in DE_CATEGORIES for ev in cats[cat]["evidence"].values()
            for src in ev)
        self.assertTrue(wiki_seen, "mindestens eine Wikipedia-Quelle nötig")


class DeVocabCollisions(unittest.TestCase):
    def test_no_collision_with_german_buzzwords_or_en_categories(self):
        o = _ontology()
        cats = _categories(o)
        existing = {w.lower() for w in
                    o["signals"]["multilingual"]["german"]["buzzwords"]}
        for cat, data in cats.items():
            if cat in DE_CATEGORIES:
                continue
            existing |= {p.lower() for p in data["items"]}
        for cat in DE_CATEGORIES:
            for phrase in cats[cat]["items"]:
                self.assertNotIn(phrase.lower(), existing,
                                 f"Kollision: {cat}:{phrase}")


class DeVocabDetection(unittest.TestCase):
    def test_classifier_picks_up_de_phrases(self):
        clf = SlopClassifier(ONTOLOGY)
        text = ("Am Ende des Tages zeigt sich: Studien belegen, dass die "
                "digitale Landschaft eine nahtlose Integration erlaubt. "
                "Es ist wichtig zu beachten, dass Experten zufolge ein "
                "facettenreiches Vorgehen nötig ist. Hier ist, was Sie "
                "wissen müssen, kurz gesagt.")
        result = clf.classify_text(text)
        hit_cats = set(result.phrase_report)
        self.assertTrue(hit_cats & set(DE_CATEGORIES), result.phrase_report)

    def test_english_clean_corpus_never_hits_de_layer(self):
        clf = SlopClassifier(ONTOLOGY)
        for item in _clean_items():
            if item.get("lang", "en") != "en":
                continue
            result = clf.classify_text(item["text"])
            self.assertFalse(set(result.phrase_report) & set(DE_CATEGORIES),
                             f"{item['id']}: {result.phrase_report}")


if __name__ == "__main__":
    unittest.main()
