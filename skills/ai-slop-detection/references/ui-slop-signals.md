# UI Slop Signals (visual, detect-only)

Reference for **AI-default UI** in generated landing pages and front-ends.
Derived from [mshumer/unslop](https://github.com/mshumer/unslop) `profiles/react-design.md`
(20 HTML samples + screenshots, MIT) — re-expressed as ontology checks. See upstream issue #15.

Scope: **detect-only**. Each hit is evidence for a human to check, not a scored signal.
The full layout-clustering detector (unslop-style sample comparison) is a separate, larger step.

## 1. Layout structure (screenshot check)

- Fixed top navbar: logo left, 3–4 links, single CTA button right; frosted-glass nav chrome
- Standard SaaS stack: hero → stats/proof strip → features → pricing → testimonials → closing CTA
- Centered hero headline block in a max-width column with two buttons underneath
- Stats row or logo/trust strip reflex-added under the hero
- Pricing as three vertical cards, middle tier featured + "Most Popular" badge
- Testimonials: five stars, one quote, round avatar/initials chip; FAQ as identical hairline rows
- Giant viewport-height sections with sparse content; dead-air bands between sections

## 2. Copy (string literal check)

- `Trusted by …` / `Loved by …` trust lines; floating proof numbers (`2,400+`, `99.9%`, `4.9/5`)
- `Built for …`, `Everything your team needs …`, `Ready to …?` closing CTA headline
- Stock pricing headings (`Simple, honest pricing`, `Plans that scale`)
- Default CTA copy: `Get Started`, `Start Free Trial`, `Book a Demo`, `Talk to Sales`
- Title Case marketing strings in UI chrome → signal `UiSlopStartCase` (regex:
  `[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+` over label/button/i18n string literals; ≥3 consecutive
  Title Case words)

## 3. CSS properties (code check)

- `linear-gradient`/`radial-gradient` stacks; radial glows/blurred orbs behind the hero
- Indigo/purple gradient text on the key H1 word (`background-clip: text`)
- `border-radius: 9999px` pills; glassmorphism / translucent panels
- `position: fixed` + `backdrop-filter` nav recipe; subtle grid/dot/noise fillers

## image-tool prompt guideline

When analyzing a screenshot of a generated page with the `image` tool, extend the prompt with:

> Additionally check for AI-default UI: purple/indigo gradient accents, glassmorphism cards,
> 3-card feature/pricing grid with middle tier featured, centered hero with CTA button pair,
> stats/logo trust strip, generic marketing copy ("Trusted by", "Get Started").
> Report each finding with the exact element you see.

Sources: unslop README + `profiles/react-design.md`; deep/04 (unslop-I2), deep/05 (deslop-I3 for
`UiSlopStartCase`, via ericzakariasson/deslop).
