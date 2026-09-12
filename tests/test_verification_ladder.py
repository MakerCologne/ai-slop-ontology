"""Tests for src/verification_ladder.py (issue #121, L1 fixtures).

Verification Ladder: per-function evidential rungs
(asserted > tested > reachable > claimed-only > stub > synthetic-risk),
derived exclusively from the code, under-credits, never over-credits.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from verification_ladder import LADDER, analyze_module  # noqa: E402


def levels(res):
    return {f["name"]: f["level"] for f in res["functions"]}


class TestLadderOrder(unittest.TestCase):
    def test_ladder_order_matches_spec(self):
        self.assertEqual(LADDER, [
            "asserted", "tested", "reachable",
            "claimed-only", "stub", "synthetic-risk",
        ])


class TestStub(unittest.TestCase):
    def test_pass_is_stub(self):
        src = "def placeholder(x):\n    pass\n"
        res = analyze_module(src)
        self.assertEqual(levels(res)["placeholder"], "stub")

    def test_ellipsis_is_stub(self):
        src = "def placeholder(x):\n    ...\n"
        res = analyze_module(src)
        self.assertEqual(levels(res)["placeholder"], "stub")

    def test_not_implemented_is_stub(self):
        src = ("def placeholder(x):\n"
               "    raise NotImplementedError()\n")
        res = analyze_module(src)
        self.assertEqual(levels(res)["placeholder"], "stub")

    def test_docstring_only_body_is_stub(self):
        src = 'def placeholder(x):\n    """Does the thing."""\n'
        res = analyze_module(src)
        self.assertEqual(levels(res)["placeholder"], "stub")

    def test_real_body_is_not_stub(self):
        src = "def add(a, b):\n    return a + b\n"
        res = analyze_module(src)
        self.assertNotEqual(levels(res)["add"], "stub")


class TestSyntheticRisk(unittest.TestCase):
    def test_random_return_in_compute_function(self):
        src = ("import random\n"
               "def calculate_score(data):\n"
               "    return random.randint(1, 100)\n")
        res = analyze_module(src)
        self.assertEqual(levels(res)["calculate_score"], "synthetic-risk")
        self.assertTrue(res["gates"])
        self.assertEqual(res["gates"][0]["name"], "calculate_score")

    def test_hardcoded_constant_with_unused_params(self):
        src = ("def parse_config(raw):\n"
               "    return {'a': 1}\n")
        res = analyze_module(src)
        self.assertEqual(levels(res)["parse_config"], "synthetic-risk")

    def test_computed_value_is_not_synthetic(self):
        src = ("def calculate_total(items):\n"
               "    return sum(items)\n")
        res = analyze_module(src)
        self.assertNotEqual(levels(res)["calculate_total"],
                            "synthetic-risk")

    def test_constant_return_using_params_is_not_synthetic(self):
        # constant, but params flow into the value -> not synthetic
        src = ("def convert(x):\n"
               "    return x\n")
        res = analyze_module(src)
        self.assertNotEqual(levels(res)["convert"], "synthetic-risk")

    def test_random_return_without_compute_claim_is_not_flagged(self):
        src = ("import random\n"
               "def roll_die():\n"
               "    return random.randint(1, 6)\n")
        res = analyze_module(src)
        # a die roll legitimately IS random; no computation claimed
        self.assertNotEqual(levels(res)["roll_die"], "synthetic-risk")


class TestAsserted(unittest.TestCase):
    def test_module_level_assert(self):
        src = ("def add(a, b):\n"
               "    return a + b\n"
               "assert add(1, 2) == 3\n")
        res = analyze_module(src)
        self.assertEqual(levels(res)["add"], "asserted")

    def test_docstring_claim_does_not_count_as_asserted(self):
        # spec-ambiguity resolution: docstring claims are claimed-only
        src = 'def add(a, b):\n    """Adds two numbers."""\n    return a + b\n'
        res = analyze_module(src)
        self.assertNotEqual(levels(res)["add"], "asserted")


class TestTested(unittest.TestCase):
    def test_reference_from_test_source(self):
        src = ("def add(a, b):\n"
               "    return a + b\n")
        tests = ["def test_add():\n    assert add(1, 2) == 3\n"]
        res = analyze_module(src, test_sources=tests)
        self.assertEqual(levels(res)["add"], "tested")

    def test_no_test_reference_falls_through(self):
        src = "def add(a, b):\n    return a + b\n"
        res = analyze_module(src, test_sources=[
            "def test_other():\n    assert 1 == 1\n"])
        self.assertNotEqual(levels(res)["add"], "tested")


class TestReachable(unittest.TestCase):
    def test_direct_call_from_module_level(self):
        src = ("def helper():\n"
               "    return 1\n"
               "x = helper()\n")
        res = analyze_module(src)
        self.assertEqual(levels(res)["helper"], "reachable")

    def test_transitive_reachability(self):
        src = ("def a():\n"
               "    return b()\n"
               "def b():\n"
               "    return c()\n"
               "def c():\n"
               "    return 1\n"
               "a()\n")
        res = analyze_module(src)
        lv = levels(res)
        self.assertEqual(lv["a"], "reachable")
        self.assertEqual(lv["b"], "reachable")
        self.assertEqual(lv["c"], "reachable")

    def test_uncalled_function_is_not_reachable(self):
        src = 'def orphan():\n    return 1\n'
        res = analyze_module(src)
        self.assertNotEqual(levels(res)["orphan"], "reachable")

    def test_explicit_entry_points(self):
        src = "def handler():\n    return 1\n"
        res = analyze_module(src, entry_points=["handler"])
        self.assertEqual(levels(res)["handler"], "reachable")

    def test_conventional_main_entry(self):
        src = ("def main():\n"
               "    return worker()\n"
               "def worker():\n"
               "    return 1\n")
        res = analyze_module(src)
        lv = levels(res)
        self.assertEqual(lv["main"], "reachable")
        self.assertEqual(lv["worker"], "reachable")


class TestClaimedOnly(unittest.TestCase):
    def test_docstring_no_callers(self):
        src = 'def analyze(x):\n    """Analyzes the data thoroughly."""\n    return len(x)\n'
        res = analyze_module(src)
        self.assertEqual(levels(res)["analyze"], "claimed-only")

    def test_implicit_claim_no_evidence(self):
        src = "def mystery(x):\n    return x + 1\n"
        res = analyze_module(src)
        self.assertEqual(levels(res)["mystery"], "claimed-only")


class TestUnderCredit(unittest.TestCase):
    def test_best_evidence_wins_but_never_invented(self):
        # tested beats reachable; assert beats docstring claim
        src = ("def f(x):\n"
               "    return x\n"
               "def g():\n"
               "    return f(1)\n"
               "g()\n")
        tests = ["def test_f():\n    assert f(2) == 2\n"]
        res = analyze_module(src, test_sources=tests)
        lv = levels(res)
        self.assertEqual(lv["f"], "tested")
        self.assertEqual(lv["g"], "reachable")

    def test_stub_beats_tested_reference(self):
        # a stub referenced by a test is still a stub (under-credit)
        src = "def compute(x):\n    pass\n"
        tests = ["def test_compute():\n    compute(1)\n"]
        res = analyze_module(src, test_sources=tests)
        self.assertEqual(levels(res)["compute"], "stub")


class TestReportShape(unittest.TestCase):
    def test_summary_counts_and_sorting(self):
        src = ("import random\n"
               "def calculate_total(items):\n"
               "    return random.random()\n"
               "def stub_fn(x):\n"
               "    pass\n"
               "def used():\n"
               "    return 1\n"
               "used()\n")
        res = analyze_module(src)
        self.assertEqual(res["summary"]["synthetic-risk"], 1)
        self.assertEqual(res["summary"]["stub"], 1)
        self.assertEqual(res["summary"]["reachable"], 1)
        # sorted best-first
        lv_order = [f["level"] for f in res["functions"]]
        ranks = [LADDER.index(l) for l in lv_order]
        self.assertEqual(ranks, sorted(ranks))

    def test_evidence_strings_present(self):
        src = "def orphan(x):\n    return x\n"
        res = analyze_module(src)
        for f in res["functions"]:
            self.assertTrue(f["evidence"])

    def test_clean_module_has_no_gates(self):
        src = ("def total(items):\n"
               "    return sum(items)\n"
               "t = total([1, 2, 3])\n")
        res = analyze_module(src)
        self.assertEqual(res["gates"], [])


class TestSelfCheck(unittest.TestCase):
    """The module must not flag its own honest helpers as synthetic."""

    def test_self_analysis_no_gates(self):
        path = os.path.join(os.path.dirname(__file__), "..", "src",
                            "verification_ladder.py")
        with open(path) as fh:
            res = analyze_module(fh.read())
        self.assertEqual(res["gates"], [])


if __name__ == "__main__":
    unittest.main()
