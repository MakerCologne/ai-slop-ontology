"""Execute every command shown in docs/USER-GUIDE.md.

The guide marks runnable examples with ```console fences and a `$ ` prompt.
This test extracts each such command, runs it, and asserts it exits 0 — so the
documentation cannot drift away from a working CLI. `slop` is rewritten to
`python -m slopkit` so no install step is required; `pip` lines are skipped.
"""

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDE = ROOT / "docs" / "USER-GUIDE.md"


def extract_console_commands(markdown: str):
    commands = []
    for block in re.findall(r"```console\n(.*?)```", markdown, re.DOTALL):
        for line in block.splitlines():
            line = line.strip()
            if line.startswith("$ "):
                commands.append(line[2:].strip())
    return commands


class DocsExamplesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.commands = extract_console_commands(GUIDE.read_text(encoding="utf-8"))
        cls.workdir = tempfile.mkdtemp(prefix="slop-docs-")
        # Fixtures referenced by --file examples in the guide.
        (Path(cls.workdir) / "draft.md").write_text(
            "In today's rapidly evolving digital landscape, our robust holistic "
            "platform serves as a centralized hub for transformative synergy and "
            "paradigm-shifting innovation, unlocking seamless value.",
            encoding="utf-8",
        )
        (Path(cls.workdir) / "clean.md").write_text(
            "We shipped the billing page Tuesday. It cut checkout from 40s to 9s.",
            encoding="utf-8",
        )
        # A document *about* slop, for the --strip-markup example (#69).
        (Path(cls.workdir) / "handbook.md").write_text(
            "# Handbook\n\n"
            "This page explains which openers the detector looks for.\n\n"
            "```\n"
            "In today's rapidly evolving digital landscape, let us delve into "
            "the rich tapestry of seamless synergy.\n"
            "```\n\n"
            "Each entry is backed by a source and a confidence value.\n",
            encoding="utf-8",
        )
        cls.env = dict(os.environ, PYTHONPATH=str(ROOT))

    def test_found_commands(self):
        # Guard against a parser that silently matches nothing.
        self.assertGreaterEqual(len(self.commands), 15)

    def test_every_console_command_runs(self):
        py = sys.executable
        for raw in self.commands:
            if raw.startswith("pip "):
                continue  # don't install inside the test
            cmd = raw.replace("slop ", f"{py} -m slopkit ")
            with self.subTest(command=raw):
                proc = subprocess.run(
                    ["bash", "-c", cmd],
                    cwd=self.workdir,
                    env=self.env,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    proc.returncode, 0,
                    f"command failed: {raw}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}",
                )


if __name__ == "__main__":
    unittest.main()
