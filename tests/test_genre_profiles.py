"""Issue #42: genre-register profiles — false-positive guards for legitimate
styles (legal, academic, marketing, technical).

Explicit opt-in only (--genre flag / genre= parameter): no auto-detection.
A profile provides a set of exempt terms (removed from signal matching BEFORE
the metrics, like the #23 quote exemption) plus adjusted thresholds/weights
for register-conventional features. Standard texts scored without a genre
are unchanged.
"""

import os
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = os.path.join(
    os.path.dirname(__file__), "..", "skills", "ai-slop-detection", "scripts"
)
sys.path.insert(0, SCRIPTS)

import slop_scorer  # noqa: E402

LEGAL_TEXT = (
    "This agreement is entered into pursuant to the laws of the State of "
    "Delaware. The licensee shall not sublicense the software. "
    "Notwithstanding any provision to the contrary, liability is limited to "
    "the fees paid. Furthermore, the licensee must indemnify the licensor. "
    "Moreover, all disputes are resolved by arbitration. The parties "
    "acknowledge the terms herein."
)

ACADEMIC_TEXT = (
    "We measured thermal conductivity across twelve samples. The apparatus "
    "was calibrated before each run. Furthermore, the samples were stored at "
    "constant humidity. Moreover, two independent observers recorded values. "
    "The results were then analyzed statistically. Errors were estimated via "
    "bootstrap resampling. All data are available on request."
)

MARKETING_TEXT = (
    "Meet the cutting-edge platform that teams love. Our state-of-the-art "
    "engine delivers innovative features and a game-changer experience for "
    "every customer. The cutting-edge design wins awards."
)

SLOP_TEXT = (
    "In today's rapidly evolving digital landscape, it's important to note "
    "that the rich tapestry of AI tools serves as a testament to innovation. "
    "Let's dive into how these cutting-edge solutions can unlock your "
    "potential and harness the power of transformative technology."
)


class TestGenreProfiles(unittest.TestCase):
    def test_four_profiles_defined(self):
        import genre_profiles
        for name in ("legal", "academic", "marketing", "technical"):
            self.assertIn(name, genre_profiles.GENRE_PROFILES)
            prof = genre_profiles.GENRE_PROFILES[name]
            self.assertTrue(prof["exempt_terms"])
            self.assertGreater(prof["decision_threshold"], 0.40)

    def test_pursuant_to_is_legal_exempt(self):
        import genre_profiles
        self.assertIn("pursuant to", genre_profiles.GENRE_PROFILES["legal"]["exempt_terms"])

    def test_unknown_genre_raises(self):
        with self.assertRaises(ValueError):
            slop_scorer.slop_score("some text", genre="poetry")

    def test_legal_text_scores_lower_with_profile(self):
        base = slop_scorer.slop_score(LEGAL_TEXT)
        with_genre = slop_scorer.slop_score(LEGAL_TEXT, genre="legal")
        self.assertLess(with_genre["slop_score"], base["slop_score"])

    def test_academic_text_scores_lower_with_profile(self):
        base = slop_scorer.slop_score(ACADEMIC_TEXT)
        with_genre = slop_scorer.slop_score(ACADEMIC_TEXT, genre="academic")
        self.assertLess(with_genre["slop_score"], base["slop_score"])

    def test_marketing_text_scores_lower_with_profile(self):
        base = slop_scorer.slop_score(MARKETING_TEXT)
        with_genre = slop_scorer.slop_score(MARKETING_TEXT, genre="marketing")
        self.assertLess(with_genre["slop_score"], base["slop_score"])

    def test_genre_reported_in_result(self):
        result = slop_scorer.slop_score(LEGAL_TEXT, genre="legal")
        self.assertEqual(result.get("genre"), "legal")

    def test_standard_texts_unchanged_without_genre(self):
        # No genre flag: default behavior untouched — known slop still fires,
        # result has no genre key.
        base = slop_scorer.slop_score(SLOP_TEXT)
        self.assertNotIn("genre", base)
        self.assertGreaterEqual(base["slop_score"], 0.40)

    def test_genre_does_not_rescue_genuine_slop(self):
        # A genre profile softens register conventions, it must not launder
        # genuinely slop-heavy text below the decision threshold.
        result = slop_scorer.slop_score(SLOP_TEXT, genre="marketing")
        self.assertGreaterEqual(result["slop_score"], 0.40)

    def test_cli_genre_flag(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write(LEGAL_TEXT)
            path = f.name
        try:
            out = subprocess.run(
                [sys.executable, os.path.join(SCRIPTS, "slop_scorer.py"),
                 "--genre", "legal", "--file", path, "--json"],
                capture_output=True, text=True, check=True)
            import json
            result = json.loads(out.stdout)
            self.assertIn("slop_score", result)
        finally:
            os.unlink(path)

    def test_cli_unknown_genre_errors(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("text")
            path = f.name
        try:
            proc = subprocess.run(
                [sys.executable, os.path.join(SCRIPTS, "slop_scorer.py"),
                 "--genre", "nope", "--file", path],
                capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
