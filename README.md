# AI Slop Ontology

**Languages:** English (canonical) · [Deutsch](README.de.md)

A structured, agent-consumable knowledge base about the phenomenon of *AI Slop*. Consolidated from academic research (Shaib et al. 2025; Madsen & Puyt 2025; Shumailov et al. 2024), investigative journalism (404 Media; NYT; Guardian), industry research (NewsGuard; Pangram Labs), and lexicography (Merriam-Webster 2025; Oxford 2024).

**Version:** 1.0.0 | **Date:** 2026-05-20 | **License:** CC BY 4.0

Full documentation lives under [`docs/en/`](docs/en/) (English, canonical) and [`docs/de/`](docs/de/) (German). Code-facing artifacts — `ai_slop_ontology.yaml`, `ontology.json`, `ontology.ttl`, and `src/` — are English-canonical.

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

## What is AI Slop?

AI Slop is **not** simply "AI-generated content." It is a **risk profile**. Three necessary conditions must ALL be met:

1. **Generative AI is primary source** of the content
2. **Human care, curation, or verification is absent**
3. **Content is distributed unsolicited** (push, not pull)

Key insight: Carefully curated, verified, and intentionally published AI outputs are explicitly NOT slop.

## Repository Structure

```
├── README.md                     ← This file (English entry point)
├── README.de.md                  ← German entry point
├── ai_slop_ontology.yaml         ← Machine-readable YAML ontology
├── ontology.json                  ← Agent-friendly JSON (all data)
├── ontology.ttl                   ← RDF/Turtle (semantic web)
├── docs/
│   ├── en/                        ← English documentation (canonical)
│   │   ├── ai-slop-ontology-v1.0.0.md   ← Canonical document (14 sections)
│   │   ├── ontology.md                  ← Human-readable taxonomy overview
│   │   ├── ontology-structure.md        ← Property-based model & class hierarchy
│   │   ├── references.md                ← Source list (30 references)
│   │   ├── report.md                    ← Deep research report (Round 1)
│   │   ├── report-extended.md           ← Extended research (Round 2)
│   │   └── research-v0.1.md             ← v0.1 research findings
│   └── de/                        ← German documentation (parity-tracked)
│       └── … (same files as docs/en/)
├── skills/
│   └── ai-slop-detection/         ← Agent skill (English)
├── src/
│   ├── classifier.py              ← Python classifier
│   └── scorer.py                   ← Scoring engine
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

### Scoring Formula
```
weights = {critical: 1.0, high: 0.7, medium: 0.4, low: 0.2}
slop_score = min(1.0, sum(weights[s.severity] * s.confidence) / max(1, n))
is_slop = (slop_score >= 0.4) OR (any critical) OR (≥ 2 high severity)
```

### Quality Dimensions (Shaib et al. 2025)
- **Information Utility:** Density (IU1), Relevance (IU2)
- **Information Quality:** Factuality (IQ1), Bias (IQ2)
- **Style Quality:** Repetition (SQ1), Templatedness (SQ2), Coherence (SQ3), Fluency (SQ4), Verbosity (SQ5), Word Complexity (SQ6), Tone (SQ7)

### 7Vs Systemic Dimensions (Madsen & Puyt 2025)
Volume, Velocity, Variety, Value, Verification, Visibility, Virality

## Key Statistics (May 2026)

| Metric | Value | Source |
|--------|-------|--------|
| AI content farm sites | 3,006 (Mar 2026) | NewsGuard |
| New farms/month | 300–500 | NewsGuard |
| AI in Google results | 19% (Jan 2025) | Graphite |
| YouTube Kids slop | ~40% | NYT |
| Workslop recipients | 40% of employees | HBR 2025 |
| Workslop rework time | ~1h 56min/instance | HBR 2025 |
| Package hallucination rate | 19.7% | USENIX 2025 |

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
