"""Packaging contract (issue #82): the installed distribution must work.

The engine loads `src/`, the skill scripts and `ontology.json` by filesystem
path relative to the package directory. `pip install -e .` keeps the checkout
layout intact and hides that, so the repo's own CI (which runs
`python -m slopkit` from the checkout) never exercised the installed state.

Two levels of guard:

  1. Declaration test — every path the engine reaches for at runtime is
     declared as wheel content in pyproject.toml. Runs everywhere, no build,
     no network. This is the one that would have caught #82.

  2. Build test — build the wheel, unpack it, import the engine from the
     unpacked tree with the checkout NOT on sys.path and NOT as cwd, and score
     a text. Skipped when the build backend is unavailable.
"""

import os
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYPROJECT = os.path.join(ROOT, "pyproject.toml")

try:  # 3.11+
    import tomllib
except ImportError:  # pragma: no cover - 3.9/3.10
    tomllib = None

# Paths the engine resolves at runtime (slopkit/_engine.py).
RUNTIME_DATA = [
    "src",
    "skills/ai-slop-detection/scripts",
    "ontology.json",
    "AI-SLOP-ONTOLOGY.md",
]

SLOP_TEXT = (
    "In today's rapidly evolving digital landscape, it's important to note that "
    "leveraging synergies is not just a strategy, it's a necessity. This rich "
    "tapestry of innovation underscores a profound transformation. Let's delve "
    "into the multifaceted realm of seamless integration and unlock the full "
    "potential of a robust, scalable ecosystem. The journey does not end here."
)


def _wheel_targets():
    """{source path: destination inside the wheel} declared in pyproject."""
    with open(PYPROJECT, "rb") as fh:
        cfg = tomllib.load(fh)
    wheel = cfg.get("tool", {}).get("hatch", {}).get("build", {}).get(
        "targets", {}).get("wheel", {})
    return wheel.get("force-include", {})


@unittest.skipIf(tomllib is None, "tomllib requires Python 3.11+")
class DeclarationTest(unittest.TestCase):
    """The wheel must declare everything the engine loads at runtime."""

    def test_runtime_data_is_shipped(self):
        declared = _wheel_targets()
        for src in RUNTIME_DATA:
            with self.subTest(path=src):
                self.assertIn(
                    src, declared,
                    f"{src} is loaded at runtime but not shipped in the wheel "
                    f"— an installed slopkit would fail on it (#82)",
                )

    def test_shipped_paths_exist_in_the_checkout(self):
        for src in _wheel_targets():
            with self.subTest(path=src):
                self.assertTrue(
                    os.path.exists(os.path.join(ROOT, src)),
                    f"pyproject ships {src}, which does not exist",
                )

    def test_no_bundled_copy_under_version_control(self):
        """Bundling happens at build time; a checked-in copy would be a
        second source of truth (adr/0002)."""
        self.assertFalse(
            os.path.exists(os.path.join(ROOT, "slopkit", "_bundled")),
            "slopkit/_bundled must be produced by the build, never committed",
        )


def _hatchling_available():
    try:
        import hatchling  # noqa: F401
        return True
    except ImportError:
        return False


@unittest.skipUnless(_hatchling_available(), "build backend not installed")
class InstalledDistributionTest(unittest.TestCase):
    """Score a text through the engine as it is laid out inside the wheel."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        tmp = cls._tmp.name
        build = subprocess.run(
            [sys.executable, "-m", "pip", "wheel", "--no-deps",
             "--no-build-isolation", "-w", tmp, ROOT],
            capture_output=True, text=True,
        )
        if build.returncode != 0:
            cls._tmp.cleanup()
            # The backend is present (class guard), so a failing build is a
            # real defect — never a skip, or #82 hides again.
            raise AssertionError(f"wheel build failed:\n{build.stderr[-3000:]}")
        wheels = [f for f in os.listdir(tmp) if f.endswith(".whl")]
        assert wheels, "pip wheel produced no wheel"
        cls.unpacked = os.path.join(tmp, "unpacked")
        with zipfile.ZipFile(os.path.join(tmp, wheels[0])) as zf:
            zf.extractall(cls.unpacked)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def _run(self, code, cwd):
        """Run `code` with only the unpacked wheel importable."""
        env = dict(os.environ)
        env["PYTHONPATH"] = self.unpacked
        env.pop("SLOP_REPO_ROOT", None)
        env.pop("SLOP_ONTOLOGY", None)
        return subprocess.run(
            [sys.executable, "-c", code], cwd=cwd, env=env,
            capture_output=True, text=True,
        )

    def test_engine_scores_from_the_installed_layout(self):
        with tempfile.TemporaryDirectory() as outside:
            proc = self._run(
                "from slopkit._engine import get_engine\n"
                "r = get_engine().classify_text(%r)\n"
                "print(round(r.overall_slop_score, 3))\n" % SLOP_TEXT,
                cwd=outside,
            )
        self.assertEqual(
            proc.returncode, 0,
            f"installed engine raised:\n{proc.stderr[-2000:]}",
        )
        self.assertGreater(
            float(proc.stdout.strip()), 0.40,
            "installed engine no longer detects a textbook slop paragraph",
        )

    def test_cli_subcommands_run_from_the_installed_layout(self):
        with tempfile.TemporaryDirectory() as outside:
            target = os.path.join(outside, "sample.txt")
            with open(target, "w", encoding="utf-8") as fh:
                fh.write(SLOP_TEXT)
            for argv in (["score", "sample.txt"], ["classify", "sample.txt"],
                         ["rhetoric", "sample.txt"], ["info"]):
                with self.subTest(command=argv[0]):
                    proc = self._run(
                        "import sys; sys.argv = ['slop'] + %r\n"
                        "from slopkit.cli import main; sys.exit(main())" % argv,
                        cwd=outside,
                    )
                    self.assertEqual(
                        proc.returncode, 0,
                        f"slop {argv[0]} failed:\n{proc.stderr[-2000:]}",
                    )

    def test_repo_only_subcommands_fail_with_a_message_not_a_traceback(self):
        """benchmark/selfcheck need the checkout; outside it they must say so."""
        with tempfile.TemporaryDirectory() as outside:
            for cmd in ("benchmark", "selfcheck"):
                with self.subTest(command=cmd):
                    proc = self._run(
                        "import sys; sys.argv = ['slop', %r]\n"
                        "from slopkit.cli import main; sys.exit(main())" % cmd,
                        cwd=outside,
                    )
                    self.assertNotIn("Traceback", proc.stderr)
                    self.assertNotEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
