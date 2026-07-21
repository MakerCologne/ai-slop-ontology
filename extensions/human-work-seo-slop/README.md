# Human, Work and SEO Slop Extension

Experimental extension module for the AI Slop Ontology.

## Files

- `human_work_seo_slop.json` — machine-readable classes, dimensions, rules, exclusions and sources
- `human_work_seo_slop.ttl` — RDF/Turtle class layer
- `RESEARCH.md` — deep research and design rationale
- `examples.json` — labeled examples and counterexamples

## Key design decisions

- The established term **AI Workslop** keeps its narrow AI-generated meaning.
- `WorkSlopFamily` is a generation-neutral grouping class.
- `HumanSlop`, `HumanWorkSlop`, `ManagementSlop` and most management subtypes are explicitly marked as **grounded extensions**, not established scientific terms.
- `SEOSlop` is generation-neutral and grounded in Google Search spam-policy categories.
- Every type contains exclusions to reduce false positives.
- Candidate terms remain in a registry until evidence supports promotion.

Run the extension validation with:

```bash
python3 -m unittest tests.test_human_work_seo_extension
```
