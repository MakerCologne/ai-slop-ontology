"""Tests for markdown markup anomalies (issue #28) — detect-only."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from markup_anomalies import find_markup_anomalies


def fired(text):
    return {s["id"] for s in find_markup_anomalies(text)["signals"]}


class HeadingLevelJumpTests(unittest.TestCase):
    def test_double_jump_fires(self):
        text = "# Title\n\n## Section\n\n#### Deep dive for no reason\n\nBody text.\n"
        self.assertIn("HeadingLevelJump", fired(text))

    def test_incremental_levels_do_not_fire(self):
        text = "# Title\n\n## Section\n\n### Subsection\n\nBody text.\n"
        self.assertNotIn("HeadingLevelJump", fired(text))

    def test_level_decrease_is_fine(self):
        text = "# Title\n\n### Subsection\n\n## Back up one level\n\nBody text.\n"
        self.assertNotIn("HeadingLevelJump", fired(text))


class ThematicBreakTests(unittest.TestCase):
    def test_excessive_breaks_fire(self):
        text = "\n".join(
            [f"Paragraph {i} with some words here.\n\n---\n" for i in range(5)]
        )
        self.assertIn("ExcessiveThematicBreaks", fired(text))

    def test_few_breaks_do_not_fire(self):
        text = "# Title\n\nIntro paragraph.\n\n---\n\nSecond paragraph with more words.\n"
        self.assertNotIn("ExcessiveThematicBreaks", fired(text))


class TitleCaseHeadingTests(unittest.TestCase):
    def test_title_case_headings_fire(self):
        text = (
            "# Overview Of The System\n\n"
            "## Installation Steps For Users\n\n"
            "### Configuration Options Available\n\n"
            "Body text follows here.\n"
        )
        self.assertIn("TitleCaseHeadings", fired(text))

    def test_sentence_case_headings_do_not_fire(self):
        text = (
            "# Overview of the system\n\n"
            "## Installation steps for users\n\n"
            "### Configuration options available\n\n"
            "Body text follows here.\n"
        )
        self.assertNotIn("TitleCaseHeadings", fired(text))


class TableMisuseTests(unittest.TestCase):
    def test_single_row_table_fires(self):
        text = (
            "Some intro text.\n\n"
            "| Option | Value |\n"
            "|--------|-------|\n"
            "| width  | 42    |\n\n"
            "Outro text.\n"
        )
        self.assertIn("SingleRowTable", fired(text))

    def test_multi_row_table_does_not_fire(self):
        text = (
            "Some intro text.\n\n"
            "| Option | Value |\n"
            "|--------|-------|\n"
            "| width  | 42    |\n"
            "| height | 13    |\n\n"
            "Outro text.\n"
        )
        self.assertNotIn("SingleRowTable", fired(text))


class BoldDensityTests(unittest.TestCase):
    def test_bold_mid_sentence_density_fires(self):
        text = (
            "This paragraph uses **bold** in one sentence. "
            "And it uses **more** bold in the next sentence. "
            "It also puts **emphasis** here again for effect. "
            "Finally **one more** bolded word closes the run.\n\n"
            "A second normal paragraph without any emphasis at all follows here.\n"
        )
        self.assertIn("BoldMidSentenceDensity", fired(text))

    def test_sparing_bold_does_not_fire(self):
        text = (
            "This paragraph uses one **bold** word and then continues "
            "normally for the rest of the sentences in it.\n\n"
            "A second normal paragraph without any emphasis at all follows here.\n"
        )
        self.assertNotIn("BoldMidSentenceDensity", fired(text))


if __name__ == "__main__":
    unittest.main()
