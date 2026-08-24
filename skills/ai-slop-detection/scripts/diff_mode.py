#!/usr/bin/env python3
"""Diff-mode scoring (issue #10).

Scores ONLY new/changed lines of a `git diff base..head` in the repo
context — pre-existing slop in unchanged lines is never counted (the
differential discipline of brianlovin/deslop, see deep/07).

Routing:
  - text files (.md, .markdown, .txt): slop_scorer.slop_score over the
    changed lines, stitched with a +-3-line context window where the changed
    line is a sentence FRAGMENT (context lines are only stitched in when the
    fragment clearly continues a sentence; they are never scored on their own)
  - code files (.ts/.tsx/.js/.jsx/.py/...): routed to code_slop (issue #9)
    on the head version, findings filtered to the changed line ranges
  - everything else (binaries, lock files, unknown extensions) is skipped

Guards: binary files and lock files (package-lock.json, yarn.lock, ... and
*.lock) are always skipped.

Public surface:
    scored_windows(lines, changed_indices, ctx=3) -> [(start, end), ...]
    diff_scores(base, head, repo_dir=None) -> [per-file report dicts]
"""

import re
import subprocess

TEXT_EXTS = {".md", ".markdown", ".txt"}
CODE_EXTS = {".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".java", ".rb",
             ".c", ".h", ".cpp", ".cs", ".php", ".swift", ".kt"}
LOCK_NAMES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
              "Cargo.lock", "Pipfile.lock", "composer.lock", "Gemfile.lock"}

_TERMINAL = re.compile(r'[.!?:;\"\'\u201d\)\]]\s*$')
# A previous context line clearly continues into the next one when it ends
# with a comma or with a function word mid-sentence ("that", "and", ...).
_CONTINUATION = re.compile(
    r'(?:,\s*$|\b(?:that|which|and|but|or|nor|because|while|when|if|so|as|to|of|in|on|with|by|for|the|a|an|is|are|was|were|be|been|being|has|have|will|can)\s*$)',
    re.IGNORECASE)

_HUNK = re.compile(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@')


def _stitch_up(lines, start, ctx):
    used = 0
    while start > 0 and used < ctx:
        prev = lines[start - 1].rstrip()
        if not prev or not _CONTINUATION.search(prev):
            break
        start -= 1
        used += 1
    return start


def _stitch_down(lines, end, ctx):
    used = 0
    while end + 1 < len(lines) and used < ctx:
        cur = lines[end].rstrip()
        if not cur or _TERMINAL.search(cur):
            break
        end += 1
        used += 1
    return end


def scored_windows(lines, changed_indices, ctx=3):
    """Group changed line indices into runs and extend each run by up to
    `ctx` context lines when the changed text is a sentence fragment."""
    if not changed_indices:
        return []
    changed = sorted(changed_indices)
    runs, start, prev = [], changed[0], changed[0]
    for idx in changed[1:]:
        if idx == prev + 1:
            prev = idx
            continue
        runs.append((start, prev))
        start = prev = idx
    runs.append((start, prev))
    windows = []
    for a, b in runs:
        a2 = _stitch_up(lines, a, ctx)
        b2 = _stitch_down(lines, b, ctx)
        windows.append((a2, b2))
    return windows


def _git(repo_dir, *args):
    return subprocess.run(["git", *args], cwd=repo_dir, check=True,
                          capture_output=True, text=True).stdout


def _parse_diff(diff_text):
    """Return {file: [added_line_numbers_at_head]} from a unified diff."""
    files, current, new_line = {}, None, None
    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
            files[current] = []
            new_line = 0
        elif line.startswith("@@") and current is not None:
            m = _HUNK.match(line)
            new_line = int(m.group(1))
        elif current is not None:
            if line.startswith("+"):
                files[current].append(new_line)
                new_line += 1
            elif line.startswith(" "):
                new_line += 1
    return files


def _is_lock(name):
    return name in LOCK_NAMES or name.endswith(".lock")


def _top_signals(score_result, limit=5):
    signals = score_result.get("signals", {})
    hits = list(signals.get("buzzword_hits", []))
    for cat in (signals.get("phrase_categories") or {}).values():
        hits.extend(cat)
    return hits[:limit]


def diff_scores(base: str, head: str, repo_dir: str = None) -> list:
    import os
    repo_dir = repo_dir or os.getcwd()
    import sys
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import slop_scorer
    from code_slop import analyze_code

    diff_text = _git(repo_dir, "diff", "--unified=0", base, head)
    added = _parse_diff(diff_text)
    report = []
    for name, added_lines in sorted(added.items()):
        basename = os.path.basename(name)
        if not added_lines or _is_lock(basename):
            continue
        ext = os.path.splitext(basename)[1].lower()
        try:
            content = _git(repo_dir, "show", f"{head}:{name}")
        except subprocess.CalledProcessError:
            continue  # deleted file
        if "\0" in content:
            continue  # binary guard
        if ext in TEXT_EXTS:
            lines = content.splitlines()
            windows = scored_windows(lines, [n - 1 for n in added_lines])
            texts = ["\n".join(lines[a:b + 1]) for a, b in windows]
            best, best_result = 0.0, None
            for t in texts:
                if not t.strip():
                    continue
                r = slop_scorer.slop_score(t)
                if r["slop_score"] >= best:
                    best, best_result = r["slop_score"], r
            entry = {"file": name, "kind": "text",
                     "slop_score": round(best, 3),
                     "lines_evaluated": len(added_lines),
                     "top_signals": _top_signals(best_result or {})}
            report.append(entry)
        elif ext in CODE_EXTS:
            result = analyze_code(content)
            # findings carry head-file line numbers; keep only those inside
            # the changed windows
            windows = scored_windows(content.splitlines(),
                                     [n - 1 for n in added_lines])
            findings = [f for f in result["findings"]
                        if any(a <= f["line"] - 1 <= b for a, b in windows)]
            report.append({"file": name, "kind": "code",
                           "slop_score": None,
                           "lines_evaluated": len(added_lines),
                           "code_findings": findings})
    return report
