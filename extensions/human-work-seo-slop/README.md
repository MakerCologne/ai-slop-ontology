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

## Verifying the citation sources

Because the ontology classifies hallucinated content, its own citations must be
checkable rather than trusted. `verify_sources.py` provides two layers:

```bash
# Offline structural checks (runs in CI, deterministic, no network):
#   - arXiv ids are well-formed and not future-dated
#   - DOIs and URLs are well-formed
#   - referenced source ids are declared; uncited sources are warned about
python3 extensions/human-work-seo-slop/verify_sources.py

# Online resolution (opt-in; also run weekly by .github/workflows/verify-sources.yml):
#   resolves every URL — HTTP 404/410 or DNS failure fails; publisher bot-blocks
#   (403/429) and timeouts are reported as inconclusive, not failures.
python3 extensions/human-work-seo-slop/verify_sources.py --online
```

The offline check is wired into the `tests` workflow; the online check runs on a
schedule so dead or fabricated links surface without making unit-test CI flaky.
