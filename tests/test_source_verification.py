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


class OnlineCoverageReporting(unittest.TestCase):
    """A run that could not check anything must not report success (§2.2)."""

    def _run(self, results, hard, verified, argv):
        original = vs.run_online
        vs.run_online = lambda sources: (results, hard, verified)
        try:
            import contextlib, io
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = vs.main(argv)
            return code, out.getvalue()
        finally:
            vs.run_online = original

    ALL_BLOCKED = {f"S{i:02d}": ("https://example.org/x", "inconclusive(URLError)")
                   for i in range(1, 21)}
    ALL_OK = {f"S{i:02d}": ("https://example.org/x", "ok") for i in range(1, 21)}

    def test_total_network_failure_fails_the_run(self):
        code, out = self._run(self.ALL_BLOCKED, [], 0, ["--online"])
        self.assertEqual(code, 1)
        self.assertIn("INCONCLUSIVE", out)
        self.assertIn("0/20 verified reachable", out)
        self.assertNotIn("no dead links", out)

    def test_coverage_gate_can_be_disabled(self):
        code, out = self._run(self.ALL_BLOCKED, [], 0,
                              ["--online", "--min-verified", "0"])
        self.assertEqual(code, 0)
        self.assertIn("0/20 verified reachable", out)

    def test_full_coverage_passes_and_reports_it(self):
        code, out = self._run(self.ALL_OK, [], 20, ["--online"])
        self.assertEqual(code, 0)
        self.assertIn("20/20 verified reachable", out)
        self.assertIn("Online check passed", out)

    def test_dead_link_fails_even_at_full_coverage(self):
        results = dict(self.ALL_OK)
        results["S01"] = ("https://example.org/gone", "not_found(HTTP 404)")
        code, out = self._run(results, ["S01: gone -> HTTP 404"], 19, ["--online"])
        self.assertEqual(code, 1)
        self.assertIn("FAILED", out)


if __name__ == "__main__":
    unittest.main()
