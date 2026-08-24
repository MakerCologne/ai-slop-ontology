"""Tests for generated-docs detection (issue #31) — detect-only, code context."""

import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from generated_docs import detect_generated_docs

FILLER = (
    "# Architecture\n\n"
    "This document outlines the well-structured architecture of the system. "
    "The design is maintainable and follows standard practices.\n"
)
SPECIFIC = (
    "# Architecture\n\n"
    "Requests enter through the edge proxy (see deploy/proxy.conf) and are "
    "routed to the worker pool. Queue depth alerts page the on-call rotation.\n"
)


def git(*args, cwd):
    return subprocess.run(["git"] + list(args), cwd=cwd,
                          capture_output=True, text=True, check=True)


class GeneratedDocsTests(unittest.TestCase):
    def _repo(self, tmp, filler=True, doc="ARCHITECTURE.md", n_old_commits=6):
        repo = os.path.join(tmp, "repo")
        os.makedirs(repo)
        git("init", "-q", cwd=repo)
        git("config", "user.email", "t@t", cwd=repo)
        git("config", "user.name", "t", cwd=repo)
        # n_old_commits history before the doc lands
        for i in range(n_old_commits):
            with open(os.path.join(repo, f"f{i}.txt"), "w") as f:
                f.write(str(i))
            git("add", "-A", cwd=repo)
            git("commit", "-q", "-m", f"base {i}", cwd=repo)
        with open(os.path.join(repo, doc), "w", encoding="utf-8") as f:
            f.write(FILLER if filler else SPECIFIC)
        git("add", "-A", cwd=repo)
        git("commit", "-q", "-m", f"add {doc}", cwd=repo)
        return repo

    def test_fresh_filler_doc_fires(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(tmp)
            hits = detect_generated_docs(repo)
            self.assertEqual([h["file"] for h in hits], ["ARCHITECTURE.md"])
            self.assertEqual(hits[0]["category"], "generated-docs")
            self.assertTrue(hits[0]["filler_phrases"])

    def test_specific_content_does_not_fire(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(tmp, filler=False)
            self.assertEqual(detect_generated_docs(repo), [])

    def test_old_filler_doc_does_not_fire(self):
        # Same filler doc, but committed 6+ commits ago (not "brand new").
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(tmp)
            for i in range(6):
                with open(os.path.join(repo, f"g{i}.txt"), "w") as f:
                    f.write(str(i))
                git("add", "-A", cwd=repo)
                git("commit", "-q", "-m", f"later {i}", cwd=repo)
            self.assertEqual(detect_generated_docs(repo), [])

    def test_other_filename_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(tmp, doc="NOTES.md")
            self.assertEqual(detect_generated_docs(repo), [])

    def test_missing_repo_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(detect_generated_docs(os.path.join(tmp, "nope")), [])


if __name__ == "__main__":
    unittest.main()
