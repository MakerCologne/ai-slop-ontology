"""Type patterns need position semantics (issue #88).

`SEOContentFarmSlop` carried `here are` and `table of contents`. Two matching
patterns of one type are decisive on their own (confidence 0.8,
src/classifier.py), so ordinary technical documentation was classified as a
content farm:

    "This page lists the commands. The commands shown here are known to run.
     We keep a table of contents at the top so the sections stay findable."
    -> 0.56

Neither hit is what the pattern means. `here are` means the listicle opener
"Here are 5 ways…", not the middle of "shown here are known"; the pattern had
no way to say "clause-initial". And `table of contents` does not separate a
content farm from a handbook — both have one.

The fix has two halves, and the tests below pin both:

  1. A `^` prefix in the SSOT marks a pattern as clause-initial, expanded in
     every module that builds a term regex (same shape as the `[X]`/`[N]`
     expansion from #83).
  2. `table of contents` is dropped, because it carries no information: it
     matched 0 of 330 corpus texts while appearing in legitimate technical
     documentation, this repository's own USER-GUIDE included.
"""

import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))

import scorer as src_scorer  # noqa: E402
import slop_scorer as skill_scorer  # noqa: E402
import genre_profiles  # noqa: E402
from classifier import SlopClassifier  # noqa: E402

ONTOLOGY = os.path.join(ROOT, "ontology.json")
CORPUS = os.path.join(ROOT, "eval", "corpus.jsonl")
THRESHOLD = 0.40

PATTERN_ENGINES = [
    ("src.scorer", src_scorer),
    ("skill.slop_scorer", skill_scorer),
    ("skill.genre_profiles", genre_profiles),
]


def _type_patterns():
    with open(ONTOLOGY, encoding="utf-8") as fh:
        return json.load(fh)["signals"]["text"]["typePatterns"]["types"]


def _corpus():
    with open(CORPUS, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                row = json.loads(line)
                if "text" in row:
                    yield row


class ClauseInitialSemanticsTest(unittest.TestCase):
    """A `^` prefix means: this pattern opens a clause."""

    # (pattern, text that must match, text that must not)
    CASES = [
        ("^here are",
         "Let's dive in! Here are the things you need to know.",
         "The commands shown here are known to run."),
        ("^here are",
         "Remote work is here to stay. Here are the key takeaways.",
         "Everything you see here are examples."),
        ("^in this article",
         "In this article we look at three options.",
         "The claim in this article is unsourced."),
    ]

    def test_clause_initial_matches_and_does_not_overmatch(self):
        for pattern, positive, negative in self.CASES:
            for label, engine in PATTERN_ENGINES:
                rx = engine._term_pattern(pattern)
                with self.subTest(pattern=pattern, engine=label, case="positive"):
                    self.assertRegex(positive.lower(), rx)
                with self.subTest(pattern=pattern, engine=label, case="negative"):
                    self.assertIsNone(
                        re.search(rx, negative.lower()),
                        f"{pattern!r} must not match {negative!r}",
                    )

    def test_start_of_text_counts_as_clause_initial(self):
        rx = src_scorer._term_pattern("^here are")
        self.assertRegex("here are five ways to do it.", rx)

    def test_start_of_line_and_list_item_count(self):
        rx = src_scorer._term_pattern("^here are")
        self.assertRegex("intro:\nhere are the steps", rx)
        self.assertRegex("intro:\n- here are the steps", rx)
        self.assertRegex("intro:\n1. here are the steps", rx)

    def test_markup_lead_ins_count_as_clause_initial(self):
        """Review finding: a listicle opener under a heading is still an
        opener. Markup stripping is opt-in and the corpus is prose-only, so
        nothing else would have caught this recall gap."""
        rx = src_scorer._term_pattern("^here are")
        for label, text in [
            ("heading", "## here are 7 ways to save time"),
            ("bold", "**here are the top reasons.**"),
            ("italic", "*here are the top reasons.*"),
            ("blockquote", "> here are the top reasons."),
            ("ellipsis", "and so on… here are the reasons."),
            ("dash", "— here are the reasons."),
        ]:
            with self.subTest(lead_in=label):
                self.assertRegex(text, rx)

    def test_closing_delimiters_do_not_hide_the_sentence_boundary(self):
        """Review finding (Codex): with a closing quote or bracket between the
        full stop and the next clause, the lookbehind saw the delimiter instead
        of the punctuation — a recall regression on typographic prose, where
        the unconstrained pattern used to match."""
        rx = src_scorer._term_pattern("^here are")
        for label, text in [
            ("curly quote", "he wrote \u201cstop.\u201d here are the alternatives."),
            ("straight quote", 'he wrote "stop." here are the alternatives.'),
            ("single quote", "he wrote \u2018stop.\u2019 here are the alternatives."),
            ("paren", "(see the notes.) here are the alternatives."),
            ("bracket", "[note.] here are the alternatives."),
        ]:
            with self.subTest(delimiter=label):
                self.assertRegex(text, rx)

    def test_markup_lead_ins_do_not_open_a_clause_mid_sentence(self):
        """The lead-ins are openers, not a licence to match anywhere."""
        rx = src_scorer._term_pattern("^here are")
        self.assertIsNone(
            re.search(rx, "the commands shown here are known to run"))
        self.assertIsNone(
            re.search(rx, "everything you see here are examples"))

    def test_without_the_marker_position_is_not_constrained(self):
        """The marker is opt-in; unmarked patterns behave exactly as before."""
        rx = src_scorer._term_pattern("here are")
        self.assertRegex("the commands shown here are known", rx)

    def test_all_engines_agree(self):
        for pattern, _, _ in self.CASES:
            built = {label: e._term_pattern(pattern) for label, e in PATTERN_ENGINES}
            with self.subTest(pattern=pattern):
                self.assertEqual(
                    len(set(built.values())), 1,
                    f"engines disagree on {pattern!r}: {built}",
                )


class SsotTest(unittest.TestCase):
    """What the ontology must say after the fix."""

    def setUp(self):
        self.types = _type_patterns()

    def test_here_are_is_marked_clause_initial(self):
        seo = self.types["SEOContentFarmSlop"]["patterns"]
        self.assertIn("^here are", seo)
        self.assertNotIn("here are", seo)

    def test_table_of_contents_is_gone(self):
        self.assertNotIn(
            "table of contents",
            self.types["SEOContentFarmSlop"]["patterns"],
            "a pattern that appears equally in content farms and handbooks "
            "carries no information (#88)",
        )

    def test_every_marked_pattern_is_still_a_phrase(self):
        """`^` marks position; it must not be used as a regex escape hatch."""
        for name, spec in self.types.items():
            for pattern in spec["patterns"]:
                with self.subTest(type=name, pattern=pattern):
                    body = pattern[1:] if pattern.startswith("^") else pattern
                    self.assertNotIn("^", body)
                    self.assertTrue(body.strip(), "empty pattern")


class EvidenceTextTest(unittest.TestCase):
    """The position marker is internal syntax and must not reach the reader."""

    def test_marker_is_not_shown_in_evidence(self):
        text = ("Here are the reasons. In this article we will explore them. "
                "Top reasons follow.")
        r = SlopClassifier(ONTOLOGY).classify_text(text)
        for signal in r.signals_detected:
            with self.subTest(signal=signal.signal_id):
                self.assertNotIn(
                    "^", signal.evidence,
                    "the clause-initial marker leaked into user-facing output",
                )


class PhraseCategoryParityTest(unittest.TestCase):
    """The skill scorer's phrase table must not be broader than the SSOT.

    Review finding: `PHRASE_CATEGORIES["listicle_tells"]` carried a bare
    "here are" while the ontology has the narrower "here are [N] ways", so the
    scorer kept firing mid-sentence on the very hard negative this issue added
    — and eval/fp_baseline.json blessed the hit instead of the fix removing it.
    """

    def test_listicle_tells_matches_the_ontology(self):
        import slop_scorer
        with open(ONTOLOGY, encoding="utf-8") as fh:
            ssot = json.load(fh)["signals"]["text"]["phrases"]["categories"]
        for category in ("listicle_tells",):
            with self.subTest(category=category):
                self.assertEqual(
                    sorted(ssot[category]["items"]),
                    sorted(slop_scorer.PHRASE_CATEGORIES[category]["phrases"]),
                    f"{category}: skill copy has drifted from ontology.json",
                )

    def test_the_new_hard_negative_produces_no_phrase_hit(self):
        import slop_scorer
        row = [r for r in _corpus() if r["id"] == "clean-tech-14"]
        self.assertEqual(len(row), 1)
        result = slop_scorer.slop_score(row[0]["text"])
        self.assertLess(result["slop_score"], THRESHOLD)
        self.assertEqual(
            result.get("phrase_hits") or result.get("phrases") or [], [],
            "technical documentation still trips a phrase category",
        )


class SkillClassifierParityTest(unittest.TestCase):
    """The skill classifier must not carry a stale copy of the pattern table.

    `slop_classifier.SLOP_TYPE_PATTERNS` is a hardcoded second copy of the
    ontology's typePatterns. The #88 change to the SSOT reached three modules
    and not this one, so the benchmark pipeline — which takes the stronger of
    scorer and skill classifier — still produced the false positive after the
    fix looked complete. Nothing pinned the two lists together; this does.
    """

    def test_patterns_match_the_ontology(self):
        import slop_classifier
        ontology = _type_patterns()
        copy = slop_classifier.SLOP_TYPE_PATTERNS
        for name, spec in ontology.items():
            with self.subTest(type=name):
                self.assertIn(name, copy, "type missing from the skill copy")
                self.assertEqual(
                    list(spec["patterns"]), list(copy[name]["patterns"]),
                    f"{name}: skill copy has drifted from ontology.json",
                )

    def test_no_extra_types_in_the_copy(self):
        import slop_classifier
        ontology = _type_patterns()
        extra = [n for n, spec in slop_classifier.SLOP_TYPE_PATTERNS.items()
                 if spec["patterns"] and n not in ontology]
        self.assertEqual(extra, [], "skill copy carries types the SSOT does not")


class NoFalsePositiveOnTechnicalDocsTest(unittest.TestCase):
    """The reported case, and the shape of it."""

    def setUp(self):
        self.clf = SlopClassifier(ONTOLOGY)

    REPORTED = (
        "This page lists the commands. The commands shown here are known to run.\n\n"
        "We keep a table of contents at the top so the sections stay findable.\n"
    )

    HARD_NEGATIVES = [
        REPORTED,
        ("## Table of contents\n\n"
         "Each section below documents one subcommand. The exit codes are listed "
         "where they differ from the default, and the examples shown here are "
         "executed by the test suite on every commit.\n"),
        ("The runbook has a table of contents because it grew past twenty "
         "sections. Operators jump straight to the part they need; the ordering "
         "follows the escalation path, not the alphabet.\n"),
    ]

    def test_reported_case_is_clean(self):
        score = self.clf.classify_text(self.REPORTED).overall_slop_score
        self.assertLess(
            score, THRESHOLD,
            f"technical documentation still classified as content farm: {score}",
        )

    def test_technical_documentation_is_clean(self):
        for i, text in enumerate(self.HARD_NEGATIVES):
            with self.subTest(fixture=i):
                r = self.clf.classify_text(text)
                self.assertLess(r.overall_slop_score, THRESHOLD)
                self.assertNotIn(
                    "SEOContentFarmSlop",
                    [s.signal_id.replace("TypePattern_", "")
                     for s in r.signals_detected],
                )


class ContentFarmStillDetectedTest(unittest.TestCase):
    """Recall guard: the fix must not buy precision with recall."""

    def setUp(self):
        self.clf = SlopClassifier(ONTOLOGY)

    POSITIVES = [
        ("Buying a coffee maker is a game-changer. Let's dive in! Here are the "
         "things you need to know before buying. In this article we will explore "
         "the top reasons why."),
        ("Top reasons why remote work is here to stay. Here are the key takeaways "
         "you need to know. In this article, let's dive in and break it down."),
        ("In this article we will explore the best options. Let's dive in. "
         "Here are the top reasons this matters for you."),
    ]

    def test_real_content_farm_texts_still_flagged(self):
        for i, text in enumerate(self.POSITIVES):
            with self.subTest(fixture=i):
                types = self.clf.classify_text(text).slop_types
                self.assertIn("SEOContentFarmSlop", types)

    def test_corpus_texts_that_carried_the_type_keep_it(self):
        keep = {"slop-seo-01", "slop-listicle-01", "slop-0202-024"}
        seen = set()
        for row in _corpus():
            if row["id"] in keep:
                seen.add(row["id"])
                with self.subTest(corpus_id=row["id"]):
                    self.assertIn(
                        "SEOContentFarmSlop",
                        self.clf.classify_text(row["text"]).slop_types,
                    )
        self.assertEqual(seen, keep, "corpus fixtures went missing")


class BorderlineTest(unittest.TestCase):
    """Two cases that sit on the line, pinned deliberately."""

    def setUp(self):
        self.clf = SlopClassifier(ONTOLOGY)

    def test_one_clause_initial_hit_alone_is_not_decisive(self):
        """A single pattern records a hypothesis, never a decisive signal."""
        text = ("Here are the three migrations we ran last quarter, with the "
                "rollback that each one needed and what it cost in downtime.")
        r = self.clf.classify_text(text)
        self.assertNotIn(
            "TypePattern_SEOContentFarmSlop",
            [s.signal_id for s in r.signals_detected],
        )

    def test_listicle_opener_in_a_list_still_counts(self):
        """Clause-initial includes list items — that is where openers live."""
        text = ("Some notes on the topic:\n\n"
                "- Here are the top reasons this matters.\n"
                "- In this article we will explore each one.\n")
        self.assertIn("SEOContentFarmSlop",
                      self.clf.classify_text(text).slop_types)


if __name__ == "__main__":
    unittest.main()
