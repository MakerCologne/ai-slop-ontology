"""Held-out estimate for the benchmark (issue #85).

`eval/calibrate.py` tunes the scorer's 14 dimension weights by coordinate
ascent **on `eval/corpus.jsonl`**, and `eval/run_benchmark.py` then reports on
the same corpus. The number this project communicates everywhere —

    Pipeline P 1.0 / R 0.995 / F1 0.998

— is therefore a training-set value, and nothing said so. `slop_scorer.py`
even documents the provenance in a comment ("Calibrated 2026-07 via
eval/calibrate.py … on eval/corpus.jsonl"), which makes the omission an
oversight rather than a dispute.

docs/SCORE-GOVERNANCE.md carries this exact case as its own cautionary tale
(ADR-0005 / #41: "eine Metrik, die nur gegen sich selbst misst, wird zur
Goodhart-Falle"). The corpus gained hard negatives; the train/test identity
stayed.

What the tests below pin:

  * folds are stratified, deterministic and genuinely disjoint — a text is
    never scored by weights that were fitted on it;
  * the fitted engine (skill-scorer) is reported apart from the unfitted ones
    (type-pattern classifier), because the unfitted part otherwise masks the
    fitted part's overfit — that masking is the whole reason the in-sample
    number looked so healthy;
  * in-sample and held-out appear side by side, never one alone.

Cost note: a real calibration run is an L3 operation (roughly 200 s per
coordinate-ascent round per fold). The machinery is therefore exercised with
an injected calibrator; the expensive end-to-end path has its own opt-in test.
"""

import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "eval"))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))

import run_benchmark  # noqa: E402

CORPUS = os.path.join(ROOT, "eval", "corpus.jsonl")
EVALS_DOC = os.path.join(ROOT, "docs", "EVALS.md")
SKILL_DOC = os.path.join(ROOT, "skills", "ai-slop-detection", "SKILL.md")


def _corpus():
    with open(CORPUS, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip() and "text" in json.loads(l)]


def _stub_calibrator(items, **kwargs):
    """Stand-in for coordinate ascent: records what it was shown."""
    _stub_calibrator.seen.append({i["id"] for i in items})
    return {"weights": {"density": 0.15}, "metrics": {}}


class FoldTest(unittest.TestCase):
    """Folds must be disjoint, complete, stratified and reproducible."""

    def setUp(self):
        self.items = _corpus()

    def test_folds_partition_the_corpus(self):
        folds = run_benchmark.make_folds(self.items, k=5, seed=17)
        self.assertEqual(len(folds), 5)
        covered = []
        for train, test in folds:
            with self.subTest(size=len(test)):
                self.assertEqual(set(train) & set(test), set(),
                                 "train and test overlap — that is leakage")
                self.assertEqual(len(train) + len(test), len(self.items))
            covered.extend(test)
        self.assertEqual(sorted(covered), list(range(len(self.items))),
                         "every text must be held out exactly once")

    def test_folds_are_stratified(self):
        folds = run_benchmark.make_folds(self.items, k=5, seed=17)
        for i, (_, test) in enumerate(folds):
            labels = {self.items[j].get("label") for j in test}
            with self.subTest(fold=i):
                self.assertEqual(labels, {"slop", "clean"},
                                 "a fold without both labels cannot be scored")

    def test_folds_are_deterministic(self):
        a = run_benchmark.make_folds(self.items, k=5, seed=17)
        b = run_benchmark.make_folds(self.items, k=5, seed=17)
        self.assertEqual(a, b, "same seed must give the same split (M8)")
        c = run_benchmark.make_folds(self.items, k=5, seed=18)
        self.assertNotEqual(a, c, "a different seed must give a different split")

    def test_k_must_be_sane(self):
        for bad in (0, 1, -3):
            with self.subTest(k=bad):
                with self.assertRaises(ValueError):
                    run_benchmark.make_folds(self.items, k=bad, seed=17)

    def test_k_may_not_exceed_the_smallest_class(self):
        """Past that, round-robin dealing produces label-free folds, and a
        label-free fold reports a vacuous P/R/F1 instead of failing."""
        smallest = min(
            sum(1 for i in self.items if i.get("label") == label)
            for label in {i.get("label") for i in self.items})
        for bad in (smallest + 1, len(self.items) + 1):
            with self.subTest(k=bad):
                with self.assertRaises(ValueError):
                    run_benchmark.make_folds(self.items, k=bad, seed=17)
        run_benchmark.make_folds(self.items, k=smallest, seed=17)  # the edge holds


def _synthetic(n_slop, n_clean):
    return ([{"id": f"s{i}", "label": "slop", "text": "x"} for i in range(n_slop)]
            + [{"id": f"c{i}", "label": "clean", "text": "y"} for i in range(n_clean)])


class FoldGuardTest(unittest.TestCase):
    """Guards that only bite on a corpus other than the default one.

    All three came out of the review of this change, and all three are the
    same shape: the failure would have been a number, not an exception.
    """

    def test_the_smallest_class_is_chosen_by_count_not_by_name(self):
        """`min((label, count))` compares the label first, so a corpus with
        more clean than slop items picks "clean" for being alphabetically
        smaller — and then accepts a k larger than the real minority."""
        items = _synthetic(n_slop=4, n_clean=40)
        with self.assertRaises(ValueError) as caught:
            run_benchmark.make_folds(items, k=5, seed=17)
        self.assertIn("slop", str(caught.exception),
                      "the error must name the actual minority class")
        run_benchmark.make_folds(items, k=4, seed=17)  # the real bound holds

    def test_a_single_label_corpus_is_refused(self):
        with self.assertRaises(ValueError):
            run_benchmark.make_folds(_synthetic(10, 0), k=2, seed=17)

    def test_an_unknown_label_is_refused(self):
        """`evaluate` reads anything that is not "slop" as clean, so a typo
        would silently become a clean item and move the precision."""
        items = _synthetic(10, 10) + [{"id": "x", "label": "sloppy", "text": "z"}]
        with self.assertRaises(ValueError) as caught:
            run_benchmark.make_folds(items, k=2, seed=17)
        self.assertIn("sloppy", str(caught.exception))


class NoLeakageTest(unittest.TestCase):
    """The calibrator must never see the texts it will be judged on."""

    def test_calibrator_only_sees_training_folds(self):
        items = _corpus()
        _stub_calibrator.seen = []
        result = run_benchmark.cross_validate(
            items, k=3, seed=17, calibrator=_stub_calibrator)
        self.assertEqual(len(_stub_calibrator.seen), 3)
        for fold, shown in zip(result["folds"], _stub_calibrator.seen):
            held_out = set(fold["test_ids"])
            with self.subTest(fold=fold["fold"]):
                self.assertEqual(
                    shown & held_out, set(),
                    "the calibrator was shown texts from its own held-out fold",
                )


class InitializationLeakageTest(unittest.TestCase):
    """Leakage through the *initialization*, not through the training items.

    Found in review of this very change. `calibrate.calibrate` seeded its
    coordinate ascent from `slop_scorer.DEFAULT_WEIGHTS` — weights fitted on
    the whole corpus, every fold's held-out texts included. Ascent moves a
    weight only on strict improvement, so a dimension the full-corpus fit had
    already placed well simply stays there, and the fit reaches the held-out
    score even though the calibrator never saw a held-out text. The first
    measurement taken with this runner was contaminated exactly that way: the
    held-out recall came out identical to the in-sample recall, to three
    decimals, on both engines.

    `NoLeakageTest` above cannot catch this — it checks which items the
    calibrator was shown, and the answer there was correct.
    """

    def test_the_fold_start_carries_no_corpus_fit(self):
        neutral = run_benchmark.neutral_weights()
        self.assertEqual(sorted(neutral), sorted(slop_scorer_keys()),
                         "a missing dimension would raise KeyError in the scorer")
        self.assertEqual(len(set(neutral.values())), 1,
                         "a uniform start is what makes it uninformative")
        self.assertNotEqual(
            neutral, run_benchmark._default_weights(),
            "the fold start must not be the corpus-fitted weights")
        self.assertAlmostEqual(sum(neutral.values()), 1.0, places=9)

    def test_cross_validation_never_starts_the_real_calibrator_at_the_defaults(self):
        """Behavioural, not source-inspecting: intercept the real calibrator.

        An earlier version of this test asserted on the source text of
        `cross_validate`, and broke the moment the call moved into the
        multi-start helper — while the behaviour it cared about was still
        correct. A test that fails for the wrong reason is noise; one that
        passes for the wrong reason is worse.
        """
        import calibrate
        seen = []
        original = calibrate.calibrate

        def spy(train, **kwargs):
            seen.append(dict(kwargs["initial_weights"]))
            return {"weights": dict(kwargs["initial_weights"]), "metrics": {}}

        calibrate.calibrate = spy
        try:
            run_benchmark.cross_validate(_corpus()[:60], k=2, seed=17,
                                         rounds=0, starts=3)
        finally:
            calibrate.calibrate = original

        self.assertEqual(len(seen), 6, "2 folds x 3 starts must each run")
        defaults = run_benchmark._default_weights()
        neutral = run_benchmark.neutral_weights()
        for index, start in enumerate(seen):
            with self.subTest(start=index):
                self.assertNotEqual(
                    start, defaults,
                    "a fold started at the corpus-fitted weights")
                self.assertEqual(sorted(start), sorted(defaults))
        self.assertIn(neutral, seen, "the neutral start must be among them")

    def test_calibrate_defaults_to_the_shipped_weights(self):
        """The re-baseline path must keep starting where it always did."""
        import calibrate
        import inspect
        self.assertIsNone(
            inspect.signature(calibrate.calibrate)
            .parameters["initial_weights"].default)

    def test_a_partial_start_is_rejected(self):
        import calibrate
        with self.assertRaises(ValueError):
            calibrate.calibrate(_corpus()[:4], rounds=0, verbose=False,
                                initial_weights={"density": 0.1})

    def test_the_threshold_reaches_the_calibrator(self):
        """Refitting at 0.40 and reporting at 0.60 would compare two engines."""
        import calibrate
        import inspect
        self.assertIn("threshold",
                      inspect.signature(calibrate.calibrate).parameters)
        strict = calibrate.calibrate(_corpus()[:24], rounds=0, verbose=False,
                                     threshold=0.95)
        loose = calibrate.calibrate(_corpus()[:24], rounds=0, verbose=False,
                                    threshold=0.05)
        self.assertNotEqual(strict["metrics"]["tp"], loose["metrics"]["tp"],
                            "the threshold did not reach the measurement")


def slop_scorer_module():
    import slop_scorer
    return slop_scorer


def slop_scorer_keys():
    return sorted(slop_scorer_module().DEFAULT_WEIGHTS)


class PlateauTest(unittest.TestCase):
    """A single ascent from the uniform vector fits nothing.

    Second review round, and the sharper of the two findings. The
    thresholded-F1 objective is piecewise constant; the ascent accepts only a
    strict improvement from moving ONE coordinate; the uniform vector sits on
    a plateau that needs several to move together. So it stops in round one,
    unchanged — and the cross-validation measured a uniform baseline while
    reporting it as a refit.

    That is an optimizer failure, not a fact about the weights, and the
    difference matters: the first version of this change concluded from the
    absent move that "the calibration is worth one text". The test below is
    the counter-example that killed that conclusion.
    """

    def test_a_better_vector_exists_where_one_ascent_cannot_reach_it(self):
        import calibrate
        items = _corpus()
        neutral = run_benchmark.neutral_weights()
        shipped = run_benchmark._default_weights()
        better = 0
        for number, (train_idx, _) in enumerate(
                run_benchmark.make_folds(items, k=5, seed=17)):
            train = [items[i] for i in train_idx]
            a = calibrate.metrics(neutral, train)["f1"]
            b = calibrate.metrics(shipped, train)["f1"]
            with self.subTest(fold=number):
                self.assertGreaterEqual(b, a - 1e-9)
            if b > a + 1e-9:
                better += 1
        self.assertGreaterEqual(
            better, 3,
            "if no better vector beat uniform on the training folds, the "
            "absent ascent move would be evidence rather than an artefact — "
            "and the plateau machinery below would be unnecessary")

    def test_restarts_are_seeded_from_the_fold_not_the_corpus(self):
        a = run_benchmark.random_start(0, 1)
        self.assertEqual(a, run_benchmark.random_start(0, 1), "not reproducible")
        self.assertNotEqual(a, run_benchmark.random_start(0, 2))
        self.assertNotEqual(a, run_benchmark.random_start(1, 1))
        self.assertEqual(sorted(a), slop_scorer_keys())
        for value in a.values():
            with self.subTest(value=value):
                self.assertIn(value, run_benchmark.CANDIDATE_VALUES)

    def test_the_first_start_is_the_neutral_one(self):
        """Restart 0 is uniform, so multi-start can only ever improve on the
        single-start result — it never trades the conservative baseline away."""
        import inspect
        source = inspect.getsource(run_benchmark._multi_start)
        self.assertIn("neutral_weights() if index == 0", source)

    def test_multi_start_keeps_the_best_training_objective(self):
        import calibrate
        items = _corpus()[:60]
        calls = []

        def fake_calibrate(train, rounds, verbose, initial_weights, threshold):
            calls.append(dict(initial_weights))
            return {"weights": dict(initial_weights), "metrics": {}}

        chosen = run_benchmark._multi_start(
            fake_calibrate, calibrate, items, rounds=1, verbose=False,
            threshold=0.40, starts=4, fold=0)["weights"]
        self.assertEqual(len(calls), 4, "every restart must actually run")
        scores = [calibrate.objective(calibrate.metrics(w, items, 0.40), 0.95)
                  for w in calls]
        best = calibrate.objective(
            calibrate.metrics(chosen, items, 0.40), 0.95)
        self.assertAlmostEqual(best, max(scores), places=9)


class CalibratorRunsTest(unittest.TestCase):
    """The calibrator must actually run.

    Found while building the cross-validation: `eval/calibrate.py` kept its own
    13-key copy of the weight names, while the scorer grew a 14th
    (`portability`, #14). Every run therefore died with
    `KeyError: 'portability'` — the script the shipped weights cite as their
    provenance could not be executed at all. Same class of defect as #88: a
    hardcoded second copy that fell behind the source.
    """

    def test_weight_keys_match_the_scorer(self):
        import calibrate
        import slop_scorer
        self.assertEqual(
            sorted(calibrate.WEIGHT_KEYS), sorted(slop_scorer.DEFAULT_WEIGHTS),
            "calibrate tunes a different set of dimensions than the scorer has",
        )

    def test_a_short_calibration_run_completes(self):
        import calibrate
        items = _corpus()[:12]
        result = calibrate.calibrate(items, rounds=1, verbose=False)
        self.assertIn("weights", result)
        self.assertEqual(sorted(result["weights"]),
                         sorted(calibrate.WEIGHT_KEYS))


class ReportingTest(unittest.TestCase):
    """In-sample and held-out side by side; fitted apart from unfitted."""

    @classmethod
    def setUpClass(cls):
        _stub_calibrator.seen = []
        cls.result = run_benchmark.cross_validate(
            _corpus(), k=3, seed=17, calibrator=_stub_calibrator)

    def test_reports_both_kinds_of_number(self):
        for key in ("in_sample", "held_out"):
            with self.subTest(key=key):
                self.assertIn(key, self.result)
                self.assertIn("skill-scorer", self.result[key])

    def test_separates_fitted_from_unfitted_engines(self):
        self.assertIn("skill-scorer", self.result["fitted"])
        for engine in ("src-classifier",):
            with self.subTest(engine=engine):
                self.assertIn(engine, self.result["unfitted"])
        self.assertEqual(
            set(self.result["fitted"]) & set(self.result["unfitted"]), set())

    def test_the_report_states_the_feature_leakage_limit(self):
        """The weights are held out; the feature inventories are not.

        `check_ssot.py` registers BUZZWORD_TIERS and PHRASE_CATEGORIES as
        corpus-calibrated, and SKILL.md says the Batch-F phrases were mined
        from the corpus's own false negatives. A fold can therefore be
        rewarded by signals designed after looking at its texts. Refitting
        weights per fold does not undo that, so the caveat has to travel with
        the number rather than live in a document beside it.
        """
        text = run_benchmark.format_cross_validation(self.result).lower()
        for token in ("weights only", "phrase_categories", "#107"):
            with self.subTest(token=token):
                self.assertIn(token, text)

    def test_the_pipeline_is_marked_as_mixed(self):
        """The pipeline takes the stronger of a fitted and an unfitted engine,
        so its held-out number understates the overfit. Saying so is the
        point of the ticket."""
        self.assertIn("skill-pipeline (scorer+classifier)", self.result["mixed"])

    def test_every_fold_reports_its_size_and_weights(self):
        for fold in self.result["folds"]:
            with self.subTest(fold=fold["fold"]):
                self.assertGreater(fold["n_train"], 0)
                self.assertGreater(fold["n_test"], 0)
                self.assertIn("weights", fold)


class EngineClassificationTest(unittest.TestCase):
    """Every benchmarked engine must be classified before it is reported.

    The in-sample headline survived for a release because nobody had to say,
    per engine, whether its number was fitted. Making that a required field
    rather than a default is the structural half of the fix.
    """

    def test_every_benchmark_engine_is_classified(self):
        for report in run_benchmark.run():
            with self.subTest(engine=report["engine"]):
                self.assertIn(
                    run_benchmark.engine_kind(report["engine"]),
                    ("fitted", "unfitted", "mixed"))

    def test_an_unclassified_engine_is_an_error_not_a_guess(self):
        with self.assertRaises(KeyError):
            run_benchmark.engine_kind("some-engine-added-later")

    def test_the_classes_do_not_overlap(self):
        names = (run_benchmark.FITTED_ENGINES + run_benchmark.UNFITTED_ENGINES
                 + run_benchmark.MIXED_ENGINES)
        self.assertEqual(len(names), len(set(names)))


class CliTest(unittest.TestCase):
    def test_flag_exists_and_is_documented(self):
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "eval", "run_benchmark.py"), "--help"],
            capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--cross-validate", proc.stdout)

    def test_stdout_carries_the_report_and_nothing_else(self):
        """`--cv-rounds 0` skips coordinate ascent, so this costs ~25 s.

        The calibrator prints minutes of progress per fold. On stdout that
        progress would break `--json` and any parse of the text report, so it
        belongs on stderr — pinned here because the leak is invisible in a
        terminal, where both streams look the same.
        """
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "eval", "run_benchmark.py"),
             "--cross-validate", "2", "--cv-rounds", "0", "--json"],
            capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(proc.returncode, 0, proc.stderr[-2000:])
        payload = json.loads(proc.stdout)  # fails loudly on any leaked line
        for key in ("in_sample", "held_out", "folds", "fitted", "unfitted",
                    "mixed"):
            with self.subTest(key=key):
                self.assertIn(key, payload)

    def test_a_noop_calibrator_reproduces_the_neutral_weights_exactly(self):
        """Fold plumbing must add nothing of its own.

        With a calibrator that tunes nothing, every fold scores with exactly
        the neutral weights, so the pooled held-out confusion must equal a
        single direct run of those weights over the whole corpus. Any
        difference is a bug in the splitting or pooling rather than a finding
        about generalization.

        (This replaces an earlier "held-out == in-sample" control, whose
        premise died when the merge base became the neutral start — in-sample
        uses the calibrated weights, the folds no longer do.)
        """
        items = _corpus()
        result = run_benchmark.cross_validate(
            items, k=2, seed=17,
            calibrator=lambda train, **kw: {"weights": {}, "metrics": {}})
        neutral = run_benchmark.neutral_weights()
        direct = run_benchmark.evaluate(
            "skill-scorer",
            lambda t: slop_scorer_module().slop_score(
                t, weights=neutral)["slop_score"],
            items, run_benchmark.DEFAULT_THRESHOLD)
        pooled = result["held_out"]["skill-scorer"]
        for key in ("tp", "fp", "tn", "fn"):
            with self.subTest(cell=key):
                self.assertEqual(pooled[key], direct[key])
        self.assertEqual(sum(pooled[k] for k in ("tp", "fp", "tn", "fn")),
                         len(items), "every text must be scored exactly once")

    def test_plain_run_is_unchanged(self):
        """Cross-validation is opt-in; the default report must not change."""
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "eval", "run_benchmark.py")],
            capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(proc.returncode, 0)
        self.assertNotIn("held-out", proc.stdout.lower())


class DocumentationTest(unittest.TestCase):
    """docs/EVALS.md must say which published number is of which kind (#70)."""

    def setUp(self):
        with open(EVALS_DOC, encoding="utf-8") as fh:
            self.doc = fh.read()

    def test_evals_names_the_in_sample_caveat(self):
        lowered = self.doc.lower()
        for token in ("in-sample", "held-out", "--cross-validate"):
            with self.subTest(token=token):
                self.assertIn(token, lowered)

    def test_the_published_figures_match_a_fresh_run(self):
        """DoD 4: the documented number must match the measuring instruction.

        `skills/ai-slop-detection/SKILL.md` publishes the benchmark as the
        skill's own headline. Found while writing this test: it claimed
        `n=314 = 221 slop + 93 clean` while the corpus had grown to 331
        (110 clean). P/R/F1 happened to survive the growth — recall does not
        depend on clean items and precision stayed at 1.0 — so no gate and no
        reader would have noticed. Pinning the whole tuple, not just the
        headline ratios, is what makes the drift visible.
        """
        with open(SKILL_DOC, encoding="utf-8") as fh:
            skill = fh.read()
        reports = {r["engine"]: r for r in run_benchmark.run()}
        scorer = reports["skill-scorer"]
        items = _corpus()
        n_slop = sum(1 for i in items if i.get("label") == "slop")
        n_clean = sum(1 for i in items if i.get("label") == "clean")

        claim = re.search(
            r"n=(\d+) = (\d+) slop \+ (\d+) clean", skill)
        self.assertIsNotNone(claim, "SKILL.md no longer states the corpus size")
        self.assertEqual(
            [int(g) for g in claim.groups()], [len(items), n_slop, n_clean],
            "SKILL.md states a corpus size the corpus does not have")

        figures = re.search(
            r"\*\*P ([\d.]+) / R ([\d.]+) / F1 ([\d.]+)\*\* "
            r"\(TP (\d+), FN (\d+), FP (\d+)\)", skill)
        self.assertIsNotNone(figures, "SKILL.md no longer states P/R/F1")
        self.assertEqual(
            [float(figures.group(i)) for i in (1, 2, 3)],
            [scorer["precision"], scorer["recall"], scorer["f1"]],
            "SKILL.md publishes figures a fresh benchmark run does not produce")
        self.assertEqual(
            [int(figures.group(i)) for i in (4, 5, 6)],
            [scorer["tp"], scorer["fn"], scorer["fp"]],
            "SKILL.md publishes a confusion matrix the run does not produce")

    def test_evals_states_the_corpus_size_the_corpus_has(self):
        """EVALS.md carried `314 Texte` in its L3 artifact list while the same
        document's new section said 331 — the stale-number defect this change
        set out to fix, inside the document that documents the fix."""
        items = _corpus()
        stale = re.findall(r"(\d+) Texte", self.doc)
        self.assertTrue(stale, "EVALS.md no longer states a corpus size")
        for claimed in stale:
            with self.subTest(claimed=claimed):
                self.assertEqual(int(claimed), len(items))

    def test_the_published_figure_is_labelled_in_sample(self):
        """An unlabelled number is the defect (#85), wherever it is published."""
        for path in (SKILL_DOC, EVALS_DOC):
            with open(path, encoding="utf-8") as fh:
                doc = fh.read()
            with self.subTest(doc=os.path.basename(path)):
                if "F1 0." not in doc:
                    continue
                self.assertRegex(
                    doc, r"(?i)in.?sample",
                    f"{os.path.basename(path)} publishes a benchmark figure "
                    "without saying it is an in-sample value")

    def test_evals_names_which_engines_are_fitted(self):
        self.assertIn("calibrate.py", self.doc)
        self.assertRegex(
            self.doc, r"(?i)nicht gefittet|ungefittet|unfitted",
            "the doc must name which part of the pipeline is not fitted",
        )


if __name__ == "__main__":
    unittest.main()
