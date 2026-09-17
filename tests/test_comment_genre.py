"""Issue #231 / P4: Genre-Profil comment + engagement_comment_default.

Abnahmekriterien:
- >= 1 True Positive fuer engagement_comment_default
- >= 2 Hard Negatives (inkl. der legitimen Control-Set-Texte = FP-Rate-0-Nachweis)
- Genre-Profil Opt-in ohne Auto-Detect (ADR-0004)
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

import genre_profiles  # noqa: E402
import slop_scorer  # noqa: E402
from rhetorical_patterns import (  # noqa: E402
    RHETORICAL_PATTERNS,
    find_rhetorical_patterns,
)

CONTROL_SET = os.path.join(ROOT, "eval", "control_set.jsonl")


def ids(text):
    return {p["id"] for p in find_rhetorical_patterns(text)}


class EngagementCommentDefaultTest(unittest.TestCase):
    # --- True Positives: die 4/4- und 3/4-Sequenz ---
    def test_tp_full_sequence_german(self):
        self.assertIn("engagement_comment_default", ids(
            "Danke für diesen spannenden Beitrag! Sie beschreiben sehr treffend, "
            "wie Führungskräfte unter Dauererreichbarkeit leiden. Ein weiterer "
            "Aspekt ist die Rollenklarheit im Team. Wie sehen Sie das?"))

    def test_tp_full_sequence_english(self):
        self.assertIn("engagement_comment_default", ids(
            "Great post, thank you for sharing! You describe the hiring problem "
            "perfectly. One more thing to add is retention. What are your thoughts?"))

    def test_tp_three_of_four_paraphrase_addon_question(self):
        # Lob fehlt, aber Paraphrase -> Ergaenzung -> Frage = 3/4 in Reihenfolge.
        self.assertIn("engagement_comment_default", ids(
            "Sie schreiben, dass Procurement-Prozesse zu langsam sind. Ein weiterer "
            "Aspekt ist der Einkauf. Wie stehen Sie dazu?"))

    def test_confidence_is_detect_only_and_at_most_half(self):
        meta = RHETORICAL_PATTERNS["engagement_comment_default"]
        self.assertLessEqual(meta["confidence"], 0.5)

    # --- Hard Negatives: legitime Kommentare feuern NICHTS (FP-Rate 0) ---
    def test_hn_substantive_disagreement(self):
        self.assertEqual(ids(
            "Ich widerspreche dem Fazit: Die Ausfallzeiten sind bei uns seit Q1 "
            "nicht gestiegen, sondern von 2,1 % auf 1,4 % gefallen, nachdem wir "
            "die Wartungsfenster gebündelt haben."), set())

    def test_hn_genuine_detail_question(self):
        # Enthaelt eine echte Frage MIT Inhalt — aber keine Sequenz.
        self.assertNotIn("engagement_comment_default", ids(
            "Welche Puffergröße verwenden Sie für die Synthese bei 40 °C? Bei uns "
            "bricht die Ausbeute ab 250 mL ab, und ich vermute den Rührereinsatz "
            "als Ursache."))

    def test_hn_two_elements_are_not_the_template(self):
        # Paraphrase + Frage allein = 2 Elemente -> kein Feuer.
        self.assertNotIn("engagement_comment_default", ids(
            "In Ihrem Beitrag fehlt mir der Hinweis auf die Netzbetreiber. Welche "
            "Wartezeiten sehen Sie dort aktuell?"))

    def test_control_set_hard_negatives_have_zero_findings(self):
        # FP-Rate-0-Nachweis auf dem Control-Set: alle 5 legitimen
        # Kommentar-Texte duerfen KEIN einziges rhetorisches Signal feuern.
        with open(CONTROL_SET) as f:
            items = [json.loads(l) for l in f if l.strip()]
        negatives = [i for i in items if i["id"].startswith("neg-comment-")]
        self.assertGreaterEqual(len(negatives), 5)
        for item in negatives:
            self.assertEqual(
                ids(item["text"]), set(),
                f"{item['id']} fired a signal: {ids(item['text'])}")
            score = slop_scorer.slop_score(item["text"])["slop_score"]
            self.assertLess(score, 0.15, f"{item['id']} scored {score}")

    def test_control_set_slop_comments_all_detected(self):
        with open(CONTROL_SET) as f:
            items = [json.loads(l) for l in f if l.strip()]
        slop = [i for i in items if i["id"].startswith("comment-slop-")]
        self.assertGreaterEqual(len(slop), 5)
        undetected = [i["id"] for i in slop
                      if "engagement_comment_default" not in ids(i["text"])]
        self.assertEqual(undetected, [],
                         "CommentSlop-Texte ohne engagement_comment_default")


class CommentGenreProfileTest(unittest.TestCase):
    # --- Opt-in, kein Auto-Detect (ADR-0004) ---
    def test_comment_and_message_profiles_defined(self):
        for name in ("comment", "message"):
            self.assertIn(name, genre_profiles.GENRE_PROFILES)
            prof = genre_profiles.GENRE_PROFILES[name]
            self.assertTrue(prof["exempt_terms"])
            self.assertGreater(prof["decision_threshold"], 0.40)

    def test_opt_in_only_no_autodetect(self):
        # Ohne --genre wird kein Profil aktiv: das Ergebnis traegt kein
        # genre-Feld (ADR-0004: Opt-in, kein Auto-Detect).
        baseline = slop_scorer.slop_score(
            "Danke für diesen spannenden Beitrag! Viele Grüße.")
        self.assertNotIn("genre", baseline)  # kein Profil automatisch aktiv

    def test_unknown_genre_raises(self):
        with self.assertRaises(ValueError):
            slop_scorer.slop_score("text", genre="comment-autodetect")

    def test_opt_in_accepts_comment_profile(self):
        result = slop_scorer.slop_score(
            "Danke für den Hinweis. Viele Grüße.", genre="comment")
        self.assertEqual(result.get("genre"), "comment")


if __name__ == "__main__":
    unittest.main()
