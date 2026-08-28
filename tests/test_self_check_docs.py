"""Meta self-check (issue #48): run the scorer against our own documentation.

A detector whose own documentation trips its own signals is an attackable
narrative. #33 checks foreign instruction files; nothing checked ours.

The gate scores every Markdown document in the repository through the #69
pre-pass (quoted material is evidence, not slop — the #23 exemption in
document form) and fails when one is at or above the decision threshold.

Documents that legitimately carry catalogue material in running prose — a
changelog listing the phrases it added, a review quoting the buzzwords it
found — are registered with a reason and a pinned ceiling, the same shape as
eval/fp_baseline.json. Registered is not exempt: the ceiling makes a document
that gets worse fail.
"""

import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "self_check_docs.py")
REGISTER = os.path.join(ROOT, "eval", "self_check_docs.json")
STYLE_DOC = os.path.join(ROOT, "docs", "DOC-STYLE.md")


def _run(*args):
    return subprocess.run(
        [sys.executable, SCRIPT, *args],
        cwd=ROOT, capture_output=True, text=True,
    )


class GateTest(unittest.TestCase):
    def test_repository_documentation_passes_the_gate(self):
        proc = _run()
        self.assertEqual(
            proc.returncode, 0,
            f"the detector flags its own documentation:\n{proc.stdout}\n{proc.stderr}",
        )

    def test_json_output_reports_every_document(self):
        proc = _run("--json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertGreaterEqual(len(payload["documents"]), 20)
        for entry in payload["documents"]:
            self.assertIn("path", entry)
            self.assertIn("score", entry)
            self.assertIn("budget", entry)

    def test_the_core_documents_are_clean_without_an_exception(self):
        """README and friends must pass on their merits, not by registration."""
        payload = json.loads(_run("--json").stdout)
        by_path = {e["path"]: e for e in payload["documents"]}
        for rel in ("README.md", "ONTOLOGY.md", "AI-SLOP-ONTOLOGY.md",
                    "docs/USER-GUIDE.md", "skills/ai-slop-detection/SKILL.md"):
            with self.subTest(document=rel):
                self.assertIn(rel, by_path)
                self.assertFalse(
                    by_path[rel]["registered"],
                    f"{rel} must pass without an exception entry",
                )
                self.assertLess(by_path[rel]["score"], 0.40)


class RegisterTest(unittest.TestCase):
    def setUp(self):
        with open(REGISTER, encoding="utf-8") as fh:
            self.register = json.load(fh)

    def test_every_exception_carries_a_reason(self):
        for path, entry in self.register["exceptions"].items():
            with self.subTest(document=path):
                self.assertTrue(
                    entry.get("reason", "").strip(),
                    f"{path} is registered without a reason",
                )
                self.assertIsInstance(entry.get("max_score"), float)

    def test_every_registered_document_exists(self):
        for path in self.register["exceptions"]:
            with self.subTest(document=path):
                self.assertTrue(os.path.exists(os.path.join(ROOT, path)))

    def test_a_registered_document_that_gets_worse_fails(self):
        """The ceiling is a ratchet, not a blanket permission."""
        payload = json.loads(_run("--json").stdout)
        for entry in payload["documents"]:
            if entry["registered"]:
                with self.subTest(document=entry["path"]):
                    self.assertLessEqual(
                        entry["score"], entry["budget"],
                        "registered ceiling exceeded",
                    )
                    self.assertLessEqual(
                        entry["score"] + 0.05, entry["budget"] + 0.05,
                        "ceiling must track the measured value, not sit far above it",
                    )

    def test_no_unused_exceptions(self):
        """A document that became clean must lose its exception."""
        payload = json.loads(_run("--json").stdout)
        by_path = {e["path"]: e for e in payload["documents"]}
        stale = [
            path for path in self.register["exceptions"]
            if by_path.get(path, {}).get("score", 1.0) < payload["threshold"]
        ]
        self.assertEqual(
            stale, [],
            f"these documents pass on their own now — drop the exception: {stale}",
        )


class StyleRuleTest(unittest.TestCase):
    def test_the_style_rule_is_written_down(self):
        self.assertTrue(
            os.path.exists(STYLE_DOC),
            "#48 asks for a documentation style rule for the repo",
        )
        with open(STYLE_DOC, encoding="utf-8") as fh:
            text = fh.read()
        for topic in ("#23", "#69", "self_check_docs"):
            with self.subTest(topic=topic):
                self.assertIn(topic, text)


class FailureModeTest(unittest.TestCase):
    def test_a_slop_document_fails_the_gate(self):
        """The gate must be able to fail — verified against a planted file."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            planted = os.path.join(tmp, "planted.md")
            with open(planted, "w", encoding="utf-8") as fh:
                fh.write(
                    "# Notes\n\n"
                    "In today's rapidly evolving digital landscape, it's important "
                    "to note that leveraging synergies is not just a strategy, it's "
                    "a necessity. This rich tapestry of innovation underscores a "
                    "profound transformation. Let's delve into the multifaceted "
                    "realm of seamless integration and unlock the full potential of "
                    "a robust, scalable ecosystem. The journey does not end here.\n"
                )
            proc = _run("--path", planted)
            self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
            self.assertIn("planted.md", proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
