#!/usr/bin/env python3
"""Meta self-check (issue #48): score this repository's own documentation.

A detector whose own documentation trips its own signals is an attackable
narrative — and until #69 there was no way to even measure it, because the
quoted examples in every document scored as prose (README stood at 0.90).

What this does:

  1. Collects the repository's Markdown documents.
  2. Runs each through the #69 pre-pass, so quoted material — code fences,
     example lists, tables, blockquotes — is evidence, not prose. This is the
     #23 quote exemption applied at document level.
  3. Fails when a document reaches the decision threshold.

Documents that carry catalogue material in *running prose* — a changelog
naming the phrases it added, a review quoting the buzzwords it found — cannot
be fixed by stripping markup without falsifying them. They are registered in
eval/self_check_docs.json with a reason and a pinned ceiling, in the shape of
eval/fp_baseline.json. Registered is not exempt: the ceiling is a ratchet, so
a registered document that gets worse still fails, and one that becomes clean
loses its entry.

Usage:
    python scripts/self_check_docs.py            # gate, exit 1 on breach
    python scripts/self_check_docs.py --json     # machine-readable
    python scripts/self_check_docs.py --path X   # check one file
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))

import markup_prepass  # noqa: E402
from classifier import SlopClassifier  # noqa: E402

REGISTER_PATH = os.path.join(ROOT, "eval", "self_check_docs.json")
THRESHOLD = 0.40

# Where the repository keeps prose. Research dumps and vendored material are
# not ours to style.
DOC_GLOBS = [
    "*.md",
    "docs/*.md",
    "adr/*.md",
    "lexikon/*.md",
    "skills/*/*.md",
]


def collect_documents():
    import glob
    seen, out = set(), []
    for pattern in DOC_GLOBS:
        for path in sorted(glob.glob(os.path.join(ROOT, pattern))):
            rel = os.path.relpath(path, ROOT)
            if rel not in seen:
                seen.add(rel)
                out.append(rel)
    return out


def load_register():
    with open(REGISTER_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def score_document(clf, path: str) -> float:
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    return clf.classify_text(markup_prepass.strip_markup(raw)).overall_slop_score


def run(paths=None) -> dict:
    register = load_register()
    exceptions = register["exceptions"]
    clf = SlopClassifier(os.path.join(ROOT, "ontology.json"))

    documents = []
    for given in (paths if paths is not None else collect_documents()):
        absolute = os.path.abspath(os.path.join(ROOT, given))
        # Normalise to the repo-relative form the register is keyed by, so
        # `--path ./CHANGELOG.md` and `--path /abs/CHANGELOG.md` find the same
        # entry as the full run does. A path outside the repo keeps its own
        # name and simply has no entry.
        rel = os.path.relpath(absolute, ROOT)
        if rel.startswith(os.pardir):
            rel = given
        entry = exceptions.get(rel)
        budget = entry["max_score"] if entry else THRESHOLD
        score = round(score_document(clf, absolute), 4)
        documents.append({
            "path": rel,
            "score": score,
            "budget": budget,
            "registered": entry is not None,
            "reason": entry["reason"] if entry else None,
            "passed": score < budget if entry is None else score <= budget,
        })
    return {"threshold": THRESHOLD, "documents": documents}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--path", action="append", dest="paths",
                        help="check this file instead of the repository")
    args = parser.parse_args()

    results = run(args.paths)
    breaches = [d for d in results["documents"] if not d["passed"]]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for d in results["documents"]:
            mark = "FAIL" if not d["passed"] else ("reg " if d["registered"] else "ok  ")
            print(f"  [{mark}] {d['score']:.3f} / {d['budget']:.3f}  {d['path']}")
        if breaches:
            print("\nSELF-CHECK FAILED — the detector flags its own documentation:",
                  file=sys.stderr)
            for d in breaches:
                print(f"  {d['path']}: {d['score']:.3f} >= budget {d['budget']:.3f}",
                      file=sys.stderr)
            print("\nFix the prose, or — if the document must quote catalogue "
                  "material in running text — register it in "
                  "eval/self_check_docs.json with a reason. See docs/DOC-STYLE.md.",
                  file=sys.stderr)
        else:
            n = len(results["documents"])
            reg = sum(1 for d in results["documents"] if d["registered"])
            print(f"\nSELF-CHECK PASSED ({n} documents, {reg} registered "
                  f"with a reason, threshold {THRESHOLD})")

    return 1 if breaches else 0


if __name__ == "__main__":
    sys.exit(main())
