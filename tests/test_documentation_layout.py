"""
Documentation must exist once (review 2026-08 §3.2).

`docs/de/` used to hold byte-identical copies of nine German root documents —
about 2,000 duplicated lines kept in step by a hand-maintenance rule, which had
already started to fail. These tests keep the layout honest: no duplicates, no
claim that a German document is English.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GERMAN_MARKERS = re.compile(
    r"\b(und|der|die|das|nicht|werden|wird|für|über|zwischen|kann)\b", re.I)
ENGLISH_MARKERS = re.compile(
    r"\b(the|and|is|are|not|with|between|for|about|can)\b", re.I)


def markdown_files(folder):
    return sorted(p for p in (ROOT / folder).rglob("*.md"))


def normalized(path):
    return path.read_text(encoding="utf-8").strip()


class TestNoDuplicateDocuments(unittest.TestCase):
    def test_docs_folders_do_not_copy_root_documents(self):
        root_docs = {p.name.lower(): p for p in ROOT.glob("*.md")}
        root_texts = {normalized(p): p.name for p in root_docs.values()}
        for folder in ("docs/de", "docs/en"):
            for doc in markdown_files(folder):
                text = normalized(doc)
                self.assertNotIn(
                    text, root_texts,
                    f"{doc.relative_to(ROOT)} duplicates {root_texts.get(text)} — "
                    f"link to it instead of copying it")

    def test_no_two_documents_anywhere_share_their_content(self):
        seen = {}
        for doc in ROOT.glob("**/*.md"):
            if any(part in {".git", "node_modules"} for part in doc.parts):
                continue
            text = normalized(doc)
            if len(text) < 400:          # short stubs and indexes may resemble
                continue
            if text in seen:
                self.fail(f"{doc.relative_to(ROOT)} duplicates "
                          f"{seen[text].relative_to(ROOT)}")
            seen[text] = doc


class TestLanguageClaims(unittest.TestCase):
    def test_english_index_does_not_call_german_documents_english(self):
        index = (ROOT / "docs" / "en" / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("canonical English entry points", index)
        # every document the index labels English must actually read as English
        for line in index.splitlines():
            if not line.startswith("| [") or line.rstrip().endswith("| German |"):
                continue
            for target in re.findall(r"\]\(([^)]+)\)", line):
                path = (ROOT / "docs" / "en" / target).resolve()
                if not path.is_file():
                    continue
                text = path.read_text(encoding="utf-8")[:4000]
                self.assertGreater(
                    len(ENGLISH_MARKERS.findall(text)),
                    len(GERMAN_MARKERS.findall(text)),
                    f"{path.name} is listed as English but does not read as English")

    def test_relative_links_resolve(self):
        for doc in ROOT.glob("**/*.md"):
            if any(part in {".git", "node_modules"} for part in doc.parts):
                continue
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)",
                                     doc.read_text(encoding="utf-8")):
                if target.startswith(("http", "#", "mailto:")):
                    continue
                target = target.split("#")[0]
                if not target:
                    continue
                self.assertTrue((doc.parent / target).exists(),
                                f"{doc.relative_to(ROOT)} links to missing {target}")


if __name__ == "__main__":
    unittest.main()
