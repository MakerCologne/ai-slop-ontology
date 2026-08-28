"""Markdown pre-pass (issue #69): score the prose, not the quoted examples.

The scorer matches occurrences, not speech-act roles. A document *about* slop
quotes slop, so every signal list, code fence and blockquote of examples fires
the very signals it documents. Measured on this repository before the fix:

    README.md            0.90
    ONTOLOGY.md          0.93
    AI-SLOP-ONTOLOGY.md  0.99
    docs/USER-GUIDE.md   0.995

Which is the detector contradicting its own published precision at its most
visible example, and makes every self-application (#48) uninterpretable.

Boundary (from the ticket): #23 is the content exemption at analysis time,
#28 detects markup anomalies without stripping. This is the input pre-pass.
"""

import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "src"))

import markup_prepass  # noqa: E402
from classifier import SlopClassifier  # noqa: E402

THRESHOLD = 0.40

# Documents that are *about* slop and quote it.
SELF_DOCS = [
    "README.md",
    "ONTOLOGY.md",
    "AI-SLOP-ONTOLOGY.md",
    os.path.join("docs", "USER-GUIDE.md"),
]


class StripUnitTest(unittest.TestCase):
    """What the pre-pass removes, and what it must leave alone."""

    def test_fenced_code_block_is_removed(self):
        text = (
            "Real prose that stands on its own merits.\n\n"
            "```\nlet us delve into the rich tapestry of synergy\n```\n\n"
            "More real prose here.\n"
        )
        out = markup_prepass.strip_markup(text)
        self.assertNotIn("rich tapestry", out)
        self.assertIn("Real prose", out)
        self.assertIn("More real prose", out)

    def test_tilde_fence_and_language_tag(self):
        text = "before\n\n~~~python\ndelve = 'tapestry'\n~~~\n\nafter\n"
        out = markup_prepass.strip_markup(text)
        self.assertNotIn("tapestry", out)
        self.assertIn("before", out)
        self.assertIn("after", out)

    def test_inline_code_span_is_removed(self):
        out = markup_prepass.strip_markup("The signal `rich tapestry` fires here.")
        self.assertNotIn("rich tapestry", out)
        self.assertIn("The signal", out)

    def test_blockquote_is_removed(self):
        text = "Our example:\n\n> in today's fast-paced digital landscape\n\nEnd.\n"
        out = markup_prepass.strip_markup(text)
        self.assertNotIn("fast-paced", out)
        self.assertIn("Our example", out)

    def test_table_is_removed(self):
        text = (
            "Catalogue:\n\n"
            "| signal | example |\n"
            "|---|---|\n"
            "| metaphor | a rich tapestry |\n\n"
            "Done.\n"
        )
        out = markup_prepass.strip_markup(text)
        self.assertNotIn("rich tapestry", out)
        self.assertIn("Catalogue", out)
        self.assertIn("Done", out)

    def test_quoted_example_list_is_removed(self):
        text = (
            "The phrase database contains:\n\n"
            '- "delve into"\n'
            '- "rich tapestry"\n'
            "- `navigate the landscape`\n\n"
            "Each entry carries a confidence.\n"
        )
        out = markup_prepass.strip_markup(text)
        self.assertNotIn("rich tapestry", out)
        self.assertNotIn("delve into", out)
        self.assertIn("confidence", out)

    def test_ordinary_prose_list_survives(self):
        """A list of arguments is prose, not a catalogue of examples."""
        text = (
            "Three reasons to prefer detection:\n\n"
            "- It keeps the author in charge of the text.\n"
            "- It leaves a record of what was found and why.\n"
            "- It does not need to guess who wrote the draft.\n"
        )
        out = markup_prepass.strip_markup(text)
        for line in ("keeps the author in charge",
                     "leaves a record",
                     "does not need to guess"):
            self.assertIn(line, out)

    def test_plain_text_is_returned_unchanged(self):
        text = "No markup at all, just a sentence that says something."
        self.assertEqual(markup_prepass.strip_markup(text).strip(), text)

    def test_is_idempotent(self):
        text = "a\n\n```\ndelve\n```\n\n> quoted tapestry\n\nb\n"
        once = markup_prepass.strip_markup(text)
        self.assertEqual(markup_prepass.strip_markup(once), once)

    def test_unclosed_fence_strips_to_end(self):
        """A malformed document must not leak the fence content."""
        out = markup_prepass.strip_markup("intro\n\n```\nrich tapestry forever\n")
        self.assertNotIn("rich tapestry", out)
        self.assertIn("intro", out)


class SelfApplicationTest(unittest.TestCase):
    """The repo's own documentation must read as clean prose once stripped."""

    def setUp(self):
        self.clf = SlopClassifier(os.path.join(ROOT, "ontology.json"))

    def test_own_docs_are_clean_after_the_prepass(self):
        for rel in SELF_DOCS:
            with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
                raw = fh.read()
            stripped = markup_prepass.strip_markup(raw)
            score = self.clf.classify_text(stripped).overall_slop_score
            with self.subTest(document=rel):
                self.assertLess(
                    score, THRESHOLD,
                    f"{rel} still scores {score:.3f} after the markup pre-pass "
                    f"— the detector flags its own documentation (#69)",
                )

    def test_prepass_does_not_rescue_actual_slop(self):
        """Stripping markup must not become a way to launder slop prose."""
        slop = (
            "In today's rapidly evolving digital landscape, it's important to "
            "note that leveraging synergies is not just a strategy, it's a "
            "necessity. This rich tapestry of innovation underscores a profound "
            "transformation. Let's delve into the multifaceted realm of seamless "
            "integration and unlock the full potential of a robust ecosystem. "
            "The journey does not end here — it is only the beginning."
        )
        stripped = markup_prepass.strip_markup(slop)
        self.assertGreater(
            self.clf.classify_text(stripped).overall_slop_score, THRESHOLD,
            "prose slop must stay detected after the pre-pass",
        )


class CorpusNonRegressionTest(unittest.TestCase):
    """FP guardrail: the pre-pass is opt-in and changes no corpus verdict."""

    def test_corpus_texts_are_unaffected_when_they_carry_no_markup(self):
        import json
        clf = SlopClassifier(os.path.join(ROOT, "ontology.json"))
        changed = []
        with open(os.path.join(ROOT, "eval", "corpus.jsonl"), encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                row = json.loads(line)
                if "text" not in row:
                    continue
                raw = clf.classify_text(row["text"]).overall_slop_score
                stripped_text = markup_prepass.strip_markup(row["text"])
                stripped = clf.classify_text(stripped_text).overall_slop_score
                if (raw < THRESHOLD) != (stripped < THRESHOLD):
                    changed.append((row["id"], row.get("label"), raw, stripped))
        self.assertEqual(
            changed, [],
            f"the pre-pass flips corpus verdicts: {changed}",
        )


class CliTest(unittest.TestCase):
    """--strip-markup reports raw and stripped score side by side (#69)."""

    def _slop(self, *argv, stdin=""):
        return subprocess.run(
            [sys.executable, "-m", "slopkit", *argv],
            input=stdin, capture_output=True, text=True, cwd=ROOT,
        )

    DOC = (
        "This section explains what the detector looks for.\n\n"
        "```\nlet us delve into the rich tapestry of seamless synergy\n```\n\n"
        "Each entry is backed by a source.\n"
    )

    def test_flag_prints_both_scores(self):
        proc = self._slop("score", "--strip-markup", "-", stdin=self.DOC)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("raw", proc.stdout.lower())
        self.assertIn("stripped", proc.stdout.lower())

    def test_json_output_carries_both_scores(self):
        import json
        proc = self._slop("score", "--strip-markup", "--json", "-", stdin=self.DOC)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertIn("raw_slop_score", payload)
        self.assertIn("slop_score", payload)
        self.assertLess(payload["slop_score"], payload["raw_slop_score"])

    def test_gate_uses_the_stripped_score(self):
        """--fail-over on a markdown document must judge the prose."""
        proc = self._slop("score", "--strip-markup", "--fail-over", "0.4", "-",
                          stdin=self.DOC)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_without_the_flag_behaviour_is_unchanged(self):
        import json
        proc = self._slop("score", "--json", "-", stdin=self.DOC)
        payload = json.loads(proc.stdout)
        self.assertNotIn("raw_slop_score", payload)


if __name__ == "__main__":
    unittest.main()
