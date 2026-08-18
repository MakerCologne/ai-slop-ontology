"""
The installed CLI must work outside a checkout (review 2026-08 §1.1).

`pip install .` used to produce a `slop` command that raised
ModuleNotFoundError on every subcommand, because slopkit resolved src/, the
skill scripts and ontology.json by filesystem path but packaged none of them.
These tests pin the two halves of the fix: the loader tolerates both layouts,
and the build configuration still carries the files into the wheel.
"""

import os
import sys
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

from slopkit import _engine


class TestDetectorLoading(unittest.TestCase):
    def test_load_detectors_returns_all_three(self):
        SlopClassifier, find_rhetorical, catalogue = _engine.load_detectors()
        self.assertTrue(callable(SlopClassifier))
        self.assertTrue(callable(find_rhetorical))
        self.assertGreater(len(catalogue), 0)

    def test_ontology_path_resolves(self):
        self.assertTrue(_engine.ontology_path().is_file())

    def test_env_override(self):
        os.environ["SLOP_ONTOLOGY"] = os.path.join(ROOT, "ontology.json")
        try:
            self.assertTrue(_engine.ontology_path().is_file())
        finally:
            del os.environ["SLOP_ONTOLOGY"]


class TestBuildConfiguration(unittest.TestCase):
    """Guard the force-include table — dropping an entry re-breaks the wheel."""

    REQUIRED = {
        '"src" = "slopkit/engine"',
        '"skills/ai-slop-detection/scripts" = "slopkit/skill"',
        '"ontology.json" = "slopkit/data/ontology.json"',
        '"AI-SLOP-ONTOLOGY.md" = "slopkit/data/AI-SLOP-ONTOLOGY.md"',
    }

    def test_wheel_ships_engine_skill_and_data(self):
        with open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8") as f:
            pyproject = f.read()
        self.assertIn("[tool.hatch.build.targets.wheel.force-include]", pyproject)
        for line in self.REQUIRED:
            self.assertIn(line, pyproject,
                          f"wheel would no longer ship {line}")

    def test_entry_point_is_declared(self):
        with open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8") as f:
            self.assertIn('slop = "slopkit.cli:main"', f.read())


if __name__ == "__main__":
    unittest.main()
