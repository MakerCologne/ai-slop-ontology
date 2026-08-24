#!/usr/bin/env python3
"""
Generated-docs detection (issue #31) — detect-only, code context.

Detects the classic "agent booted, immediately wrote aspirational docs"
pattern: a fresh ARCHITECTURE.md / CONTRIBUTING.md / PHILOSOPHY.md /
GOALS.md that (a) landed within the last 5 commits of the repository and
(b) contains generic filler phrases ("This document outlines",
"well-structured", "maintainable"). Both conditions must hold — an old
boilerplate CONTRIBUTING.md is boring but not a fresh artifact, and a fresh
specific doc is legitimate.

Public surface:
    detect_generated_docs(repo_path) -> list[{file, category, age_commits,
                                              filler_phrases, keep_when}]
"""

import os
import re
import subprocess

DOC_NAMES = ["ARCHITECTURE.md", "CONTRIBUTING.md", "PHILOSOPHY.md", "GOALS.md"]

FILLER_PHRASES = [
    "this document outlines",
    "well-structured",
    "maintainable",
    "this guide covers the essentials",
    "best practices outlined",
]

_RECENT_COMMITS = 5  # "younger than the last 5 commits"


def _git(*args, cwd):
    return subprocess.run(["git"] + list(args), cwd=cwd,
                          capture_output=True, text=True)


def detect_generated_docs(repo_path: str) -> list:
    hits = []
    if not os.path.isdir(repo_path):
        return hits
    # The doc must have landed within the most recent _RECENT_COMMITS commits.
    # Commit-hash membership (not timestamps — batch commits share seconds).
    recent = _git("rev-list", f"-n{_RECENT_COMMITS}", "HEAD", cwd=repo_path)
    if recent.returncode != 0 or not recent.stdout.strip():
        return hits
    recent_hashes = set(recent.stdout.split())

    for name in DOC_NAMES:
        path = os.path.join(repo_path, name)
        if not os.path.isfile(path):
            continue
        last = _git("log", "-1", "--format=%H", "--", name, cwd=repo_path)
        if last.returncode != 0 or not last.stdout.strip():
            continue  # untracked files: no commit evidence, skip (conservative)
        if last.stdout.strip() not in recent_hashes:
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                content = f.read().lower()
        except OSError:
            continue
        fillers = [p for p in FILLER_PHRASES if p in content]
        if not fillers:
            continue
        hits.append({
            "file": name,
            "category": "generated-docs",
            "age_commits": _RECENT_COMMITS,
            "filler_phrases": fillers,
            "keep_when": "A hand-written doc landing with a big refactor "
                         "that genuinely references the new structure — "
                         "specific content never fires (no filler phrases).",
        })
    return hits
