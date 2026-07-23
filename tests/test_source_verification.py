"""Deterministic (offline) tests for the extension source verifier."""

import datetime
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = os.path.join(ROOT, "extensions", "human-work-seo-slop")
sys.path.insert(0, EXT)

import verify_sources as vs


class StructureChecks(unittest.TestCase):
    AS_OF = datetime.date(2026, 7, 23)

    def test_valid_arxiv_doi_url_pass(self):
        for url in ("https://arxiv.org/abs/2412.15378",
                    "https://doi.org/10.1177/0170840618820072",
                    "https://www.betterup.com/workslop"):
            self.assertIsNone(vs.check_structure("S", url, self.AS_OF), url)

    def test_future_dated_arxiv_is_rejected(self):
        err = vs.check_structure("S", "https://arxiv.org/abs/2712.00001", self.AS_OF)
        self.assertIsNotNone(err)
        self.assertIn("future-dated", err)

    def test_malformed_ids_rejected(self):
        self.assertIsNotNone(vs.check_structure("S", "https://arxiv.org/abs/not-an-id", self.AS_OF))
        self.assertIsNotNone(vs.check_structure("S", "https://doi.org/not-a-doi", self.AS_OF))
        self.assertIsNotNone(vs.check_structure("S", "ftp://x", self.AS_OF))

    def test_arxiv_month_out_of_range(self):
        err = vs.check_structure("S", "https://arxiv.org/abs/2413.00001", self.AS_OF)
        self.assertIsNotNone(err)


class ExtensionSourcesAreValid(unittest.TestCase):
    def test_extension_sources_pass_offline(self):
        data = vs.load()
        errors, _warnings = vs.run_offline(data, datetime.date.today())
        self.assertEqual(errors, [], "structural source errors: " + "; ".join(errors))

    def test_no_arxiv_id_is_future_dated(self):
        data = vs.load()
        errors, _ = vs.run_offline(data, datetime.date.today())
        self.assertFalse([e for e in errors if "future-dated" in e])


if __name__ == "__main__":
    unittest.main()
