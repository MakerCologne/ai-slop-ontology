#!/usr/bin/env python3
"""
Empirical re-calibration loop (sampling harness) — Issue #12.

Buzzword lists age with model generations (unslop insight): model defaults
are measurable. This harness implements the loop:

  1. GENERATE  — sample N texts per (model, domain) from any
                 OpenAI-compatible chat endpoint. Offline workflows skip
                 this step and feed pre-generated samples via --samples.
  2. MINE      — n-gram / pattern repetition mining across the samples,
                 cross-checked against the current BUZZWORD_TIERS +
                 MULTILINGUAL_BUZZWORDS + PHRASE_CATEGORIES so only NEW
                 (not yet covered) candidates are proposed.
  3. INTEGRATE — the candidate list feeds calibrate.py (--sample-mine) as
                 tier-change suggestions next to the weight calibration.

Usage:
    # offline mining over pre-generated samples (tests / CI path):
    python3 eval/sample_mine.py mine --samples eval/samples.jsonl

    # live generation via an OpenAI-compatible endpoint:
    OPENAI_BASE_URL=http://host:8080/v1 OPENAI_API_KEY=... \
    python3 eval/sample_mine.py generate --model qwen --n 20 \
        --domain blog --out eval/samples.jsonl

    # mining with tier suggestion:
    python3 eval/sample_mine.py mine --samples eval/samples.jsonl --out-candidates eval/candidates.json

No network access happens unless `generate` is called with a resolvable
endpoint; `mine` is pure local computation over a JSONL file.
"""

import argparse
import json
import math
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))

import slop_scorer  # noqa: E402  (SSOT for known vocabulary)

# How many samples must repeat an n-gram before it counts as a model default.
DEFAULT_MIN_DOCS = 2
# Candidate cap — proposals stay reviewable; tier changes remain a human/
# calibration decision, never silent vocabulary growth.
DEFAULT_MAX_CANDIDATES = 40
# Ignore boilerplate n-grams shorter than this word count.
MIN_N_WORDS = 2
MAX_N_WORDS = 5

_WORD_RE = re.compile(r"[\w'äöüÄÖÜß-]+", re.UNICODE)

PROMPT_TEMPLATES = {
    "blog": "Write a short blog post (300 words) about: {topic}.",
    "docs": "Write documentation for a CLI tool flag: {topic}.",
    "summary": "Summarize the following topic for a general audience: {topic}.",
}
DEFAULT_TOPICS = [
    "teamwork", "productivity", "machine learning", "startup growth",
    "remote work", "data quality", "code review", "onboarding",
]


def tokenize(text: str) -> list:
    return [w.lower() for w in _WORD_RE.findall(text)]


def load_samples(path: str) -> list:
    items = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            # accept {"text": ...} or {"response": ...} records; keep metadata
            text = rec.get("text") or rec.get("response") or ""
            items.append({"text": text, "model": rec.get("model", "unknown"),
                          "domain": rec.get("domain", "unknown")})
    return [s for s in items if s["text"].strip()]


def known_vocabulary() -> set:
    """Terms already covered by the scorer SSOT (case-insensitive)."""
    known = set()
    for tier in slop_scorer.BUZZWORD_TIERS.values():
        for w in tier["words"]:
            known.add(w.lower())
    for words in slop_scorer.MULTILINGUAL_BUZZWORDS.values():
        for w in words:
            known.add(w.lower())
    for cat in slop_scorer.PHRASE_CATEGORIES.values():
        for w in cat.get("patterns", []) if isinstance(cat, dict) else []:
            known.add(re.sub(r"[^a-zäöüß ]", " ", w.lower()).strip())
    return known


def ngram_counts(samples: list, n: int) -> Counter:
    """Doc-frequency of word n-grams: in how many samples each appears."""
    df = Counter()
    for s in samples:
        toks = tokenize(s["text"])
        seen = set(tuple(toks[i:i + n]) for i in range(len(toks) - n + 1))
        for gram in seen:
            df[gram] += 1
    return df


def mine(samples: list, min_docs: int = DEFAULT_MIN_DOCS,
         max_candidates: int = DEFAULT_MAX_CANDIDATES) -> list:
    """Rank repeated n-grams as candidate model defaults.

    Ranking: doc-frequency first (repetition across independent samples is
    the signal), then n-gram length as tie-break (longer = more specific).
    Candidates fully contained in the known vocabulary are dropped — the
    loop proposes only what the tiers do NOT cover yet.
    """
    known = known_vocabulary()
    candidates = {}
    for n in range(MIN_N_WORDS, MAX_N_WORDS + 1):
        for gram, df in ngram_counts(samples, n).items():
            if df < min_docs:
                continue
            phrase = " ".join(gram)
            if any(phrase in k or k in phrase for k in known if k):
                continue  # already covered by an existing tier entry
            score = (df, n)
            if candidates.get(phrase, (-1,))[0] < df:
                candidates[phrase] = score
    ranked = sorted(candidates.items(), key=lambda kv: (-kv[1][0], -kv[1][1], kv[0]))
    return [{"phrase": p, "doc_frequency": df, "n": n,
             "min_tier_hint": "t1" if df >= 4 else "t2"}
            for p, (df, n) in ranked[:max_candidates]]


def generate(model: str, n: int, domain: str, out: str,
             base_url: str = None, api_key: str = None,
             topics: list = None, timeout: int = 120) -> list:
    """Sample n generations from an OpenAI-compatible /chat/completions endpoint."""
    base_url = base_url or os.environ.get("OPENAI_BASE_URL")
    api_key = api_key or os.environ.get("OPENAI_API_KEY", "none")
    if not base_url:
        raise SystemExit(
            "generate needs OPENAI_BASE_URL (OpenAI-compatible endpoint) — "
            "or use `mine --samples` on pre-generated output.")
    topics = topics or DEFAULT_TOPICS
    template = PROMPT_TEMPLATES.get(domain, PROMPT_TEMPLATES["blog"])
    url = base_url.rstrip("/") + "/chat/completions"
    records = []
    for i in range(n):
        topic = topics[i % len(topics)]
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user",
                          "content": template.format(topic=topic)}],
            "temperature": 1.0,
        }).encode()
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {api_key}"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = json.load(resp)
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"sample {i + 1}/{n} failed: {e}", file=sys.stderr)
            continue
        text = body["choices"][0]["message"]["content"]
        records.append({"model": model, "domain": domain, "topic": topic,
                        "text": text})
    with open(out, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return records


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="sample from an OpenAI-compatible endpoint")
    g.add_argument("--model", required=True)
    g.add_argument("--n", type=int, default=20)
    g.add_argument("--domain", choices=sorted(PROMPT_TEMPLATES), default="blog")
    g.add_argument("--out", default=os.path.join(ROOT, "eval", "samples.jsonl"))
    g.add_argument("--base-url", default=None)

    m = sub.add_parser("mine", help="mine repeated patterns from samples")
    m.add_argument("--samples", required=True)
    m.add_argument("--min-docs", type=int, default=DEFAULT_MIN_DOCS)
    m.add_argument("--max-candidates", type=int, default=DEFAULT_MAX_CANDIDATES)
    m.add_argument("--out-candidates", default=None,
                   help="write candidate list as JSON here")
    m.add_argument("--json", action="store_true", help="machine-readable output")

    args = p.parse_args(argv)

    if args.cmd == "generate":
        records = generate(args.model, args.n, args.domain, args.out,
                           base_url=args.base_url)
        print(f"wrote {len(records)} samples to {args.out}")
        return 0

    samples = load_samples(args.samples)
    if not samples:
        print("no usable samples found", file=sys.stderr)
        return 1
    candidates = mine(samples, args.min_docs, args.max_candidates)
    if args.out_candidates:
        with open(args.out_candidates, "w", encoding="utf-8") as f:
            json.dump({"n_samples": len(samples), "candidates": candidates},
                      f, ensure_ascii=False, indent=2)
    if args.json:
        print(json.dumps({"n_samples": len(samples),
                          "candidates": candidates}, ensure_ascii=False))
    else:
        print(f"samples: {len(samples)}  new candidates: {len(candidates)}")
        for c in candidates:
            print(f"  [{c['min_tier_hint']}] df={c['doc_frequency']}  {c['phrase']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
