# AI Slop Ontology

A structured, agent-consumable knowledge base about the phenomenon of *AI Slop*. Consolidated from academic research (Shaib et al. 2025; Madsen & Puyt 2025; Shumailov et al. 2024), investigative journalism (404 Media; NYT; Guardian), industry research (NewsGuard; Pangram Labs), and lexicography (Merriam-Webster 2025; Oxford 2024).

**Version:** 1.9.0 | **Date:** 2026-08-25 | **License:** CC BY 4.0

## Quick Start

```python
import json, yaml

# Load canonical ontology
with open("ai_slop_ontology.yaml") as f:
    ontology = yaml.safe_load(f)

# Classify content
slop_score = compute_slop_score(content, modality)
if slop_score >= 0.70:
    action = "exclude_from_rag"
elif slop_score >= 0.40:
    action = "require_human_review"
else:
    action = "allow_with_checks"
```

## CLI Toolkit (`slop`)

A command-line front-end over the same engine and ontology data. No third-party
dependencies — the detector uses only the Python standard library.

```bash
pip install -e .          # exposes the `slop` command (or use `python -m slopkit`)

slop score "In today's rapidly evolving landscape, our holistic platform serves as a hub."
slop classify --file draft.md          # slop types, signals, dimensions, actions
slop rhetoric "It's not a tool. It's a movement."   # named AI writing patterns
echo "text" | slop check -             # combined score + rhetorical report (stdin)
slop code --lang python app.py         # slop patterns in source code
slop info                              # signal-database + ontology metadata
slop benchmark                         # run the labelled-corpus benchmark
slop selfcheck                         # JSON/TTL/YAML/skill consistency check
```

| Command | Output |
|---------|--------|
| `score` | numeric slop score (0–1) + severity |
| `classify` | full report: slop types, weighted signals, dimensions, countermeasures |
| `rhetoric` | detect-only rhetorical patterns as named evidence (not scored) |
| `check` | `classify` + `rhetoric` in one pass |
| `code` | code-specific slop (hallucinated packages, hardcoded secrets, comment bloat) |
| `info` / `benchmark` / `selfcheck` | metadata / evaluation / consistency |

Diff mode and code-slop checker (issues #9/#10, Batch D):

```bash
python3 skills/ai-slop-detection/scripts/slop_scorer.py --diff main..feature   # scores ONLY new/changed lines
python3 scripts/code_slop_check.py --file src/helper.ts                  # detect-only code-slop findings
```

`--diff` evaluates text files (`.md`/`.txt`) with the text scorer and routes code
files to `code_slop.py` (see #9); binaries and lock files are skipped; changed
lines get a ±3-line context window for sentence fragments. Exit 1 when any new
slop crosses the threshold.

Every text command reads a positional string, `--file PATH`, or stdin (`-`), and
takes `--json` for machine-readable output.

📖 **Full manual with use cases and tested examples: [docs/USER-GUIDE.md](docs/USER-GUIDE.md)**

## What is AI Slop?

AI Slop is **not** simply "AI-generated content." It is a **risk profile**. Three necessary conditions must ALL be met:

1. **Generative AI is primary source** of the content
2. **Human care, curation, or verification is absent**
3. **Content is distributed unsolicited** (push, not pull)

Key insight: Carefully curated, verified, and intentionally published AI outputs are explicitly NOT slop.

## Repository Structure

```
├── AI-SLOP-ONTOLOGY.md          ← Canonical document (14 sections, versioned in front matter)
├── ai_slop_ontology.yaml        ← Machine-readable YAML ontology
├── ontology.json                 ← Agent-friendly JSON (all data)
├── ontology.ttl                  ← RDF/Turtle (semantic web)
├── ONTOLOGY.md                   ← Human-readable taxonomy overview
├── ONTOLOGY-STRUCTURE.md         ← Property-based model & class hierarchy
├── REFERENCES.md                 ← Source list (38 references)
├── CHANGELOG.md                  ← Version history
├── REVIEW-2026-07.md             ← Deep review findings (code + data audit)
├── report.md                     ← Deep research report (Round 1)
├── report-extended.md            ← Extended research (Round 2)
├── RESEARCH-v0.1.md              ← v0.1 research findings
├── pyproject.toml                ← Packaging + `slop` CLI entry point
├── slopkit/                      ← CLI toolkit (wraps src/ + rhetorical detector)
│   ├── cli.py                    ← `slop` subcommands
│   └── _engine.py                ← composed engine adapter
├── src/
│   ├── classifier.py             ← Python classifier (v1.2)
│   └── scorer.py                  ← Scoring engine
├── skills/ai-slop-detection/     ← Agent skill (self-contained scorer + classifier + rhetoric)
├── tests/                        ← Unit tests (python3 -m unittest discover tests)
└── examples/
    ├── classification-examples.json  ← 8 scored examples
    ├── text-slop-examples.json       ← Text slop instances
    ├── image-slop-examples.json      ← Image slop instances
    └── code-slop-examples.json       ← Code slop instances
```

## Ontology Architecture

### Top-Level Classes
ContentItem → SyntheticContent → AI_SlopCandidate → ConfirmedAI_Slop

Properties: hasGenerationMode, hasHumanOversightLevel, hasQualityProfile, hasDistributionPattern, hasIntent, hasProvenanceStatus, hasRiskProfile, hasSlopScore

### Classification Thresholds

| Score | Class | Agent Behavior |
|-------|-------|---------------|
| 0.00–0.24 | LowSlopRisk | Normal use, source checks still needed |
| 0.25–0.49 | ModerateSlopRisk | Use only with cross-checking |
| 0.50–0.69 | HighSlopRisk | Not as primary source, human review |
| 0.70–1.00 | AISlopCandidate | Do not cite, do not store as fact |
| any + high harm | CriticalReviewRequired | Always escalate (legal, medical, children) |

### Scoring Formula (noisy-OR since v1.2.0)
```
weights = {critical: 1.0, high: 0.7, medium: 0.4, low: 0.2}
slop_score = min(1.0, 1 − Π(1 − weights[s.severity] * s.confidence))
is_slop = (slop_score >= 0.4) OR (any critical) OR (≥ 2 high severity)
```
Independent evidence accumulates instead of being averaged away.

### Quality Dimensions (Shaib et al. 2025)
- **Information Utility:** Density (IU1), Relevance (IU2)
- **Information Quality:** Factuality (IQ1), Bias (IQ2)
- **Style Quality:** Repetition (SQ1), Templatedness (SQ2), Coherence (SQ3), Fluency (SQ4), Verbosity (SQ5), Word Complexity (SQ6), Tone (SQ7)

### 7Vs Systemic Dimensions (Madsen & Puyt 2025)
Volume, Velocity, Variety, Value, Verification, Visibility, Virality

## Key Statistics (July 2026)

| Metric | Value | Source |
|--------|-------|--------|
| AI content farm sites | 3,749 (Jun 23, 2026) | NewsGuard |
| New farms/month | 300–500 | NewsGuard |
| AI in Google results | 19% (Jan 2025) | Graphite |
| YouTube Kids slop | ~40% | NYT |
| Workslop recipients | 40% of employees | HBR 2025 |
| Workslop rework time | ~1h 56min/instance | HBR 2025 |
| Package hallucination rate | 19.7% | USENIX 2025 |
| AI share of new Deezer uploads | 44% (~75k tracks/day); 1–3% of streams, ~85% fraud | Deezer Apr 2026 |
| Spotify spam tracks removed | 75M+ (12 months to Sep 2025) | Spotify |
| Journal submissions since ChatGPT | +42%; >30% of peer reviews AI-involved | Organization Science 2026 |
| curl bug bounty AI slop | ~20% of reports; program closed Feb 2026 | Stenberg |

## New in v1.2.0

- **Labeled evaluation corpus** (`eval/corpus.jsonl`, 314 examples, 7 languages, hard-negative
g  genres legal/academic/marketing/technical/config/recipe/lyric; 66% of lines sourced from
  deep-research artifacts — see `source` field per line) and benchmark runner
  (`eval/run_benchmark.py`, per-genre FP-rate breakdown).
  Current measurement (skill-pipeline, threshold 0.40, `eval/corpus.jsonl`, 2026-08-25):
  **Precision 1.000, Recall 0.312, F1 0.476** — the enlarged corpus is substantially
  harder than the 53-example baseline (F1 0.982 there); the recall drop is concentrated
  in slop composed of throat-clearing/emphasis-crutch phrases, which are documented
  ontology gaps (research deep-dives 01–07), not corpus mislabels. Precision holds at
  1.0 across all hard-negative genres (FP rate 0.0 everywhere).
- **Calibrated weights** via `eval/calibrate.py`: skill pipeline F1 **0.47 → 0.98** at precision 1.0
- **Noisy-OR score aggregation** — independent evidence accumulates instead of being averaged away
- **New languages:** Hindi, Vietnamese, Urdu markers (closing the §12 language-bias gap)
- New phrase category `authority_claims`; TTL synchronized; consistency checker (`scripts/check_consistency.py`) wired into CI; engine parity tests

## New in v1.1.0

- **SecurityReportSlop** — AI-generated vulnerability reports (curl killed its bug bounty over these, Feb 2026)
- **PeerReviewSlop** — AI-generated peer reviews (Organization Science 2026: >30% of reviews AI-involved)
- **HyperTypicality** image signal — AI faces look "more typical than real" (ANU/PNAS 2026)
- Detection engine fixes: word-boundary matching, overlap deduplication, multilingual case fix, burstiness neutrality for short texts, severity-weighted scoring
- Test suite under `tests/`, LICENSE file, CHANGELOG

## 12 Harm Types
Model Collapse, Epistemic Pollution, Misinformation, Trust Erosion, Workplace Productivity Loss, Creator Squeeze, Harm to Children, Ad Fraud, Cognitive Load, Environmental Cost, Democracy Risk, Royalty Fraud

## Agent Integration Hooks

```python
def classify_content(content, modality) -> SlopAssessment:
    """Returns: {slop_score, is_slop, dimensions, harms, actor_hypothesis}"""

def route_by_harm(assessment) -> Action:
    """Block | Refine | Flag | Pass"""

def update_ontology(new_evidence) -> None:
    """Extend with new actor patterns, harm types, detection methods"""
```

Compatible with: LangGraph-Node, MCP-Tool, AutoGen-Function

## Sources

24+ numbered references including:
- Merriam-Webster (2025), Oxford (2024), Simon Willison (2024)
- Shaib et al. (arXiv:2509.19163), Kommers et al. (arXiv:2601.06060)
- Madsen & Puyt (SSRN:5558018), Shumailov et al. (Nature 2024)
- NewsGuard × Pangram Labs, Niederhoffer et al. (HBR 2025)
- 404 Media (Koebler), NYT, Guardian, Scientific American

## Maintenance

- **Update rhythm:** Quarterly (new model generations → new slop patterns)
- **Ad-hoc:** NewsGuard quarterly reports, new arXiv taxonomies
- **Ground truth:** [github.com/cshaib/slop](https://github.com/cshaib/slop)
- **Contributions welcome:** Audio slop research, non-Western platforms, cross-modal detection

## License

CC BY 4.0
