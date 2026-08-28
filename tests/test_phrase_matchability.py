"""Phrase matchability (issue #83): no SSOT phrase may be undetectable.

`_term_pattern()` built its regex with `re.escape()`, so the ten phrases that
carry a `[X]`/`[N]` placeholder were searched literally: "in the age of [X]"
only ever matched the literal string "in the age of [X]", never "in the age of
artificial intelligence". They counted as signals, were documented as signals,
and could not fire.

The structural test below would have caught it: for every phrase in the
ontology it builds a text the phrase is supposed to match and asserts the
engines find it. It is generic on purpose — it holds for phrases added later,
including ones with placeholder syntax nobody has thought of yet.
"""

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))

import scorer as src_scorer  # noqa: E402
import slop_scorer as skill_scorer  # noqa: E402
import genre_profiles  # noqa: E402

ONTOLOGY = os.path.join(ROOT, "ontology.json")

# Fillers used to turn a phrase template into a text it must match.
FILLERS = {"[x]": "artificial intelligence", "[n]": "5"}

# Every module that builds a term regex — the expansion must be identical in
# all of them, or genre exemptions would strip different spans than the scorer
# matches.
PATTERN_ENGINES = [
    ("src.scorer", src_scorer),
    ("skill.slop_scorer", skill_scorer),
    ("skill.genre_profiles", genre_profiles),
]

# The two that actually count occurrences (genre_profiles only strips).
MATCH_ENGINES = PATTERN_ENGINES[:2]


def _all_phrases():
    with open(ONTOLOGY, encoding="utf-8") as fh:
        ont = json.load(fh)
    cats = ont["signals"]["text"]["phrases"]["categories"]
    for name, cat in sorted(cats.items()):
        for item in cat["items"]:
            yield name, item


def _instantiate(phrase: str) -> str:
    """The phrase with placeholders filled in — a text it must match."""
    out = phrase.lower()
    for token, filler in FILLERS.items():
        out = out.replace(token, filler)
    return out


class PlaceholderExpansionTest(unittest.TestCase):
    """[X] stands for a noun phrase, [N] for a number — in every engine."""

    CASES = [
        # (phrase, text that must match, text that must not)
        ("in the age of [X]",
         "in the age of artificial intelligence, everything changed.",
         "in the age we live in, everything changed."),
        ("the future of [X] is bright",
         "the future of remote work is bright, they said.",
         "the future is bright, they said."),
        ("here are [N] ways",
         "here are 7 ways to improve your workflow.",
         "here are ways to improve your workflow."),
        ("[N] things you need to know",
         "10 things you need to know before you start.",
         "things you need to know before you start."),
        ("a sea of [X]",
         "he stood before a sea of possibilities.",
         "he stood before a sea, alone."),
    ]

    def test_placeholder_matches_and_does_not_overmatch(self):
        for phrase, positive, negative in self.CASES:
            for label, engine in PATTERN_ENGINES:
                pattern = engine._term_pattern(phrase)
                with self.subTest(phrase=phrase, engine=label, case="positive"):
                    import re
                    self.assertRegex(positive, pattern)
                with self.subTest(phrase=phrase, engine=label, case="negative"):
                    import re
                    self.assertIsNone(
                        re.search(pattern, negative),
                        f"{phrase!r} must not match {negative!r}",
                    )

    def test_number_words_count_as_numbers(self):
        pattern = src_scorer._term_pattern("top [N] reasons")
        import re
        self.assertRegex("top five reasons to switch", pattern)
        self.assertRegex("top 5 reasons to switch", pattern)

    def test_placeholder_does_not_span_sentences(self):
        """[X] is a noun phrase, not 'the rest of the document'."""
        import re
        pattern = src_scorer._term_pattern("the future of [X] is bright")
        self.assertIsNone(re.search(
            pattern,
            "the future of work. everything else is bright.",
        ))

    def test_all_engines_agree_on_the_pattern(self):
        for phrase, _, _ in self.CASES:
            patterns = {label: e._term_pattern(phrase)
                        for label, e in PATTERN_ENGINES}
            with self.subTest(phrase=phrase):
                self.assertEqual(
                    len(set(patterns.values())), 1,
                    f"engines disagree on {phrase!r}: {patterns}",
                )


class EveryPhraseIsMatchableTest(unittest.TestCase):
    """Structural guard: no phrase in the SSOT may be undetectable."""

    def test_every_phrase_matches_its_own_instantiation(self):
        for category, phrase in _all_phrases():
            text = _instantiate(phrase)
            for label, engine in MATCH_ENGINES:
                with self.subTest(category=category, phrase=phrase, engine=label):
                    hits = engine.find_term_matches(text, [phrase])
                    self.assertTrue(
                        hits,
                        f"phrase {phrase!r} ({category}) cannot match the text "
                        f"it describes — it is a dead entry in the signal "
                        f"database (#83)",
                    )

    def test_no_phrase_still_carries_an_unexpanded_placeholder(self):
        """Whatever placeholder syntax is used, it must be expanded."""
        import re
        for category, phrase in _all_phrases():
            pattern = src_scorer._term_pattern(phrase)
            with self.subTest(category=category, phrase=phrase):
                self.assertNotRegex(
                    pattern, r"\\\[\w+\\\]",
                    f"{phrase!r} keeps its placeholder escaped literally",
                )


if __name__ == "__main__":
    unittest.main()
