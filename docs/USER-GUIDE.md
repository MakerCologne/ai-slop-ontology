# AI Slop Toolkit — User Guide

Complete manual for the `slop` command-line toolkit and the `slopkit` Python
library built on the AI Slop Ontology.

Every command block marked `console` in this guide is executed automatically by
`tests/test_docs_examples.py`, so the commands shown here are known to run.

---

## Table of contents

1. [What it does](#1-what-it-does)
2. [Installation](#2-installation)
3. [Core concepts: two layers](#3-core-concepts-two-layers)
4. [Command reference](#4-command-reference)
5. [Use cases](#5-use-cases)
6. [Python library](#6-python-library)
7. [JSON output & integration](#7-json-output--integration)
8. [Exit codes](#8-exit-codes)
9. [Troubleshooting & FAQ](#9-troubleshooting--faq)

---

## 1. What it does

The toolkit answers two different questions about a piece of text:

- **"How sloppy is this?"** — a probabilistic **slop score** from 0 to 1, built
  from 233 signals (buzzwords, phrase patterns, punctuation and structural
  anomalies, multilingual markers). Use it to *gate* or *rank* content.
- **"Which AI writing tics are in this?"** — nine **rhetorical patterns** named
  with a quoted line of evidence. These are reported for a human to check and are
  deliberately **not** folded into the score.

It also classifies **source code** for hallucinated packages, hardcoded secrets,
and comment bloat.

The detection engine and ontology data use only the Python standard library — no
third-party dependencies.

---

## 2. Installation

```console
$ pip install -e .
```

This exposes the `slop` command. If you'd rather not install anything, replace
`slop` with `python -m slopkit` in any example below — both are equivalent.

Verify the install and inspect the loaded signal database:

```console
$ slop info
```

Expected output (abridged):

```text
AI Slop Ontology — AI Slop Ontology v1.2.1 (2026-07-10, CC BY 4.0)
ontology file: /path/to/ontology.json

signal database: 233 signals
  buzzwords:   107 across 4 tiers
  phrases:     114 across 7 categories
  structural:  7
  punctuation: 5
  languages:   german, french, spanish, hindi, vietnamese, urdu
  rhetorical:  9 detect-only patterns (BinaryContrast, ColonReveal, ...)
```

---

## 3. Core concepts: two layers

The toolkit is deliberately split into two layers because they answer different
questions and fail in different ways.

| Layer | Command | Output | Folded into score? |
|-------|---------|--------|--------------------|
| **Scoring** | `score`, `classify` | 0–1 score, severity, signals, slop types | — |
| **Rhetorical** | `rhetoric` | named patterns + quoted evidence | **No** |

Why keep them apart? A polished marketing sentence can be full of AI *writing
shapes* ("It's not X. It's Y.") while containing zero buzzwords — so it scores
low but is clearly AI-styled. The reverse is also true. Running both (`check`)
gives you the complete picture. See [Use case 4](#use-case-4-edit-out-ai-writing-tics).

Severity bands used by `score`/`classify`:

| Score | Severity | Suggested action |
|-------|----------|------------------|
| 0.00–0.24 | 🟢 `clean` | normal use |
| 0.25–0.39 | 🟡 `ai_assisted` | source-check recommended |
| 0.40–0.69 | 🟠 `suspicious` | human review, cross-check |
| 0.70–1.00 | 🔴 `slop_candidate` | exclude from RAG, do not cite |

---

## 4. Command reference

All text commands accept input three ways: a **positional string**, `--file PATH`,
or **stdin** (`-`). Add `--json` for machine-readable output.

```console
$ slop score "some text to score"
$ echo "piped text" | slop score -
$ slop score --file draft.md
```

| Command | Purpose |
|---------|---------|
| `slop score TEXT` | numeric score + severity (add `--fail-over N` for CI gating) |
| `slop classify TEXT` | full report: slop types, weighted signals, dimensions, actions |
| `slop rhetoric TEXT` | named rhetorical patterns with quoted evidence |
| `slop check TEXT` | `classify` + `rhetoric` in one pass (add `--fail-over N`) |
| `slop code TEXT` | code-specific slop (hallucinated packages, secrets, comment bloat) |
| `slop info` | signal-database and ontology metadata |
| `slop benchmark` | run the labelled-corpus benchmark (F1 report) |
| `slop selfcheck` | JSON/TTL/YAML/skill consistency check |

### Quoted material in Markdown

A document *about* slop quotes slop. This guide scores 0.99 verbatim, purely
because of the examples in its tables and code fences. Markdown input is
therefore stripped before scoring — fenced code, blockquotes, table rows,
inline code spans and emphasised example lists are ignored:

```console
$ slop score --file draft.md
$ slop score --file draft.md --no-strip-quotes
$ echo "text with \`quoted markers\`" | slop score - --strip-quotes
```

| Flag | Effect |
|------|--------|
| *(default)* | strip when the input is a `.md`/`.markdown`/`.mdx` file |
| `--strip-quotes` | strip regardless of input source (stdin, literal text) |
| `--no-strip-quotes` | score the document verbatim, quotations included |

`--json` reports which mode was used as `quoted_markdown_stripped`. Prose that
enumerates markers without quoting them still scores high — that is deliberate,
and the point at which a human should read the flagged lines.

Global help:

```console
$ slop --help
$ slop --version
```

---

## 5. Use cases

### Use case 1: Quick quality check of a draft

Score a suspicious paragraph:

```console
$ slop score "In today's rapidly evolving digital landscape, our robust holistic platform serves as a centralized hub, highlighting our commitment to transformative synergy."
```

```text
🔴 slop score 0.96  [███████████████████·]  slop_candidate
  top signals: CriticalBuzzword, BuzzwordOveruse_Severe
```

A grounded, specific paragraph scores clean:

```console
$ slop score "We shipped the new billing page on Tuesday. It cut checkout time from 40 seconds to 9. Two customers hit a rounding bug on refunds; a fix is in review."
```

```text
🟢 slop score 0.00  [····················]  clean
```

### Use case 2: Full classification before storing in a RAG index

Get the slop types, every weighted signal, and the recommended action:

```console
$ slop classify "In today's rapidly evolving digital landscape, it's worth noting that our robust, holistic platform serves as a centralized hub, highlighting our unwavering commitment. In conclusion, we must embrace this transformative paradigm."
```

```text
🔴 slop score 0.98  [████████████████████]  slop_candidate

signals (3):
  ⚠ BuzzwordOveruse_Severe [high 92%] — 7 unique buzzwords: robust, ...
  ⚠ CriticalBuzzword [critical 90%] — Tier1 hit(s): in today's rapidly evolving, ...
  ⚠ PhrasePattern [medium 75%] — Found: it's worth noting, in conclusion,

dimensions: Density=0.8, Repetition=0.09

recommended: exclude_from_rag, do_not_cite, label_as_ai
```

The `recommended` line maps directly to a retrieval policy: `exclude_from_rag`
means don't index it.

### Use case 3: CI content gate

`slop score --fail-over N` exits non-zero when the score reaches the threshold,
so it drops straight into a shell guard, pre-commit hook, or CI step. Clean
content passes:

```console
$ slop score --fail-over 0.7 "We shipped the billing page Tuesday. It cut checkout from 40s to 9s." && echo "PASS: content allowed"
```

```text
🟢 slop score 0.00  [····················]  clean
PASS: content allowed
```

Sloppy content is blocked (the guard catches the non-zero exit):

```console
$ slop score --fail-over 0.7 "Our robust holistic platform serves as a centralized hub for transformative synergy and paradigm-shifting innovation." || echo "BLOCKED: slop over threshold"
```

```text
🔴 slop score 0.9x  [...]  slop_candidate
BLOCKED: slop over threshold
```

### Use case 4: Edit out AI writing tics

`rhetoric` names the writing shapes with a quoted line and a suggested fix — no
score, just evidence you can act on:

```console
$ slop rhetoric "It's not just a tool. It's a movement. Our platform serves as a centralized hub, highlighting our unwavering commitment."
```

```text
✍️  rhetorical patterns (3):
  • Binary contrast (70%) — "It's not just a tool. It's"
      fix: The eval matters more than the model.
  • Superficial analysis (70%) — ", highlighting our unwavering commitment"
      fix: The launch adds file search, so users find old drafts ...
  • Fake-strong verb (60%) — "serves as a centralized hub"
      fix: The app tracks sponsors, drafts, due dates, and approvals ...
```

The power of the two-layer split shows here — this text can score **clean** on
buzzwords yet be full of AI rhetoric. `check` shows both at once:

```console
$ echo "It's not a model problem. It's a data problem. The system serves as a hub." | slop check -
```

```text
🟢 slop score 0.00  [····················]  clean
dimensions: Density=0.71, Repetition=0.18
recommended: standard_quality_check

✍️  rhetorical patterns (2):
  • Binary contrast (70%) — "It's not a model problem. It's"
  • Fake-strong verb (60%) — "serves as a hub"
```

### Use case 5: Code review for AI-generated slop

Catch a hallucinated ("slopsquatted") package in `require()`/`import` form:

```console
$ echo 'const parser = require("super-fast-json-parser");' | slop code --lang js -
```

```text
🔴 slop score 1.00  [████████████████████]  slop_candidate

signals (1):
  ⚠ InventedPackage [critical 100%] — Hallucinated packages: super-fast-json-parser
```

Catch a hardcoded secret:

```console
$ echo 'api_key = "sk-abcdef1234567890"' | slop code --lang python -
```

```text
🔴 slop score 0.9x  [...]  slop_candidate

signals (1):
  ⚠ HardcodedSecret [critical 95%] — API key or password found in code
```

### Use case 6: Multilingual detection

The scorer carries AI markers for German, French, Spanish, Hindi, Vietnamese and
Urdu. Two or more markers in one language raise a high-severity signal:

```console
$ slop score "Im heutigen schnelllebigen digitalen Zeitalter gilt es zu beachten, dass ein ganzheitlicher Ansatz die Synergieeffekte hebt und einen echten Gamechanger darstellt."
```

```text
🟠 slop score 0.49  [██████████··········]  suspicious
  top signals: Multilingual_german
```

### Use case 7: Batch-scan a folder of files

`slop` reads one document per call; loop over files in the shell and act on the
exit code:

```console
$ for f in draft.md clean.md; do slop score --fail-over 0.7 --file "$f" >/dev/null && echo "ok: $f" || echo "slop: $f"; done
```

```text
slop: draft.md
ok: clean.md
```

---

## 6. Python library

`slopkit` is importable. `get_engine()` returns a cached engine that wraps the
canonical classifier and the rhetorical detector.

```python
from slopkit import get_engine

eng = get_engine()

result = eng.classify_text("It's not a tool. It's a movement. Our platform serves as a hub.")
print(result.overall_slop_score, result.severity)   # e.g. 0.0 clean

for finding in eng.rhetorical("It's not a tool. It's a movement."):
    print(finding["id"], "→", finding["evidence"])   # BinaryContrast → It's not a tool. It's

stats = eng.signal_stats()
print(stats["total_signals"], "signals across", stats["languages"])
```

`classify_text` / `classify_code` return a `ClassificationResult` with
`overall_slop_score`, `severity`, `slop_types`, `signals_detected`,
`dimensions`, and `countermeasures`.

---

## 7. JSON output & integration

Add `--json` to `score`, `classify`, `rhetoric`, `check`, `code`, or `info` for
a stable machine-readable shape:

```console
$ slop check --json "It's not a tool. It's a movement. The platform serves as a hub."
```

```json
{
  "modality": "text",
  "slop_score": 0.0,
  "severity": "clean",
  "slop_types": [],
  "signals": [],
  "dimensions": { "Density": {"value": 0.85, "is_slop": false, "threshold": "< 0.40"} },
  "countermeasures": ["standard_quality_check"],
  "rhetorical_patterns": [
    {"id": "BinaryContrast", "label": "Binary contrast", "confidence": 0.7,
     "evidence": "It's not a tool. It's", "fix": "..."},
    {"id": "FakeStrongVerb", "label": "Fake-strong verb", "confidence": 0.6,
     "evidence": "serves as a hub", "fix": "..."}
  ]
}
```

Pipe it into `jq`, a policy engine, or a data pipeline. The `score` command's
JSON is the minimal `{"slop_score", "severity"}` pair.

---

## 8. Exit codes

| Situation | Exit code |
|-----------|-----------|
| Command succeeded | `0` |
| `score`/`check` with `--fail-over N` and score ≥ N | `1` |
| Ontology file could not be loaded | `2` |
| `benchmark`/`selfcheck` reported a failure | non-zero (propagated) |

Without `--fail-over`, `score` and `check` always exit `0` — they report, they
don't gate.

---

## 9. Troubleshooting & FAQ

**`slop: command not found`** — either run `pip install -e .` from the repo root,
or use `python -m slopkit` instead.

**"cannot load ontology"** — the engine looks for `ontology.json` in the repo
root. Point it elsewhere with `--ontology PATH` or the `SLOP_ONTOLOGY` env var.

**A clean-looking sentence scored 0 but I expected slop.** That's the two-layer
design: the *score* is buzzword/structure-driven. Run `slop rhetoric` (or
`slop check`) to surface AI *writing shapes* that the score intentionally
ignores.

**Why isn't rhetoric part of the score?** A named pattern with a quoted line is
evidence a human can verify; a probability is a guess. Mixing them would make the
score jumpy and the evidence less trustworthy. They stay separate on purpose.

**Does it detect AI authorship?** No. It detects slop *signals* and *patterns*.
It never claims a human or a model wrote something.

---

*This guide is part of the [AI Slop Ontology](../README.md). The rhetorical
pattern set is adapted from [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop) (MIT).*
