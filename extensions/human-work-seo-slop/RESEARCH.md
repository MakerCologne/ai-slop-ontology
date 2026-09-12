# Deep Research: Human, Work, Management and SEO Slop

**Status:** Experimental ontology extension  
**Version:** 0.1.0  
**Date:** 2026-07-21  
**Scope:** Human Slop, Work Slop, Management Slop, SEO Slop and evidence-backed adjacent slop types

## Executive summary

The established meaning of **AI slop** is technology-specific: low-quality digital content produced, usually at scale, by artificial intelligence. Extending the word *slop* to human work therefore requires care. The literature does **not** yet provide a broadly accepted construct called “Human Slop” or “Management Slop.”

This extension treats those terms as **grounded ontology proposals**, not settled scientific labels. It preserves the established meaning of **AI Workslop** and introduces a technology-neutral `WorkSlopFamily` that can group human-authored, AI-assisted and synthetic failure modes without claiming that they are identical.

The common mechanism is not “bad work.” It is a pattern of:

1. **superficial competence** — the item looks legitimate, polished or complete;
2. **weak goal contribution** — it does little to advance the stated objective;
3. **effort transfer** — interpretation, checking, coordination or cleanup is shifted to others;
4. **organizational or distributional amplification** — the item is mandated, repeated, scaled or privileged by a system.

For SEO, the strongest boundary comes from Google’s current spam policies: scaled content abuse is defined by low user value and ranking manipulation **regardless of how the content was created**. This makes SEO Slop a good technology-neutral family.

## Terminology status

| Term | Status in this extension | Basis |
|---|---|---|
| `AIWorkslop` | Established | BetterUp Labs and Stanford Social Media Lab explicitly define and measure it |
| `HumanSlop` | Grounded extension | New umbrella, based on slop theory plus organizational-burden research |
| `HumanWorkSlop` | Grounded extension | New subtype separating generation mode from work form |
| `ManagementSlop` | Grounded extension | New subtype grounded in organizational bullshit, red tape, administrative burden and ineffective-meeting research |
| `SEOSlop` | Grounded extension | New umbrella grounded in official search-spam categories |
| `HiringSlop` | Emerging | Phrase used in current reporting on AI application floods |
| `OpenSourceContributionSlop` | Emerging | Current empirical research describes an AI-DDoS burden on maintainers |
| `EducationalSlop` | Established domain use | Peer-reviewed study operationalizes slop in biomedical educational videos |
| `Slopaganda` | Emerging academic construct | Recent paper defines saturation-oriented AI propaganda |

## Ontological model

```text
SlopLikePhenomenon
├── AISlop                         # established technology-specific core
├── HumanSlop                     # proposed technology-specific sibling
│   └── HumanWorkSlop
├── WorkSlopFamily                # grouping class, generation-neutral
│   ├── AIWorkslop                # established meaning preserved
│   ├── HumanWorkSlop
│   ├── ManagementSlop
│   │   ├── StrategySlop
│   │   ├── JargonSlop
│   │   ├── MeetingSlop
│   │   ├── DecisionSlop
│   │   ├── MetricsSlop
│   │   ├── ProcessSlop
│   │   ├── AdministrativeSlop
│   │   └── ComplianceSlop
│   ├── CommunicationSlop
│   │   ├── DocumentationSlop
│   │   └── PresentationSlop
│   ├── CoordinationSlop
│   ├── ReviewSlop
│   ├── HiringSlop
│   └── OpenSourceContributionSlop
├── SEOSlop                       # generation-neutral distribution family
│   ├── ScaledContentSlop
│   ├── DoorwayPageSlop
│   ├── SiteReputationSlop
│   ├── ExpiredDomainSlop
│   ├── ScrapedRemixSlop
│   ├── SearchSaturationSlop
│   └── GEOManipulationSlop
├── EducationalSlop
└── Slopaganda
```

The hierarchy is intentionally **polyhierarchical**. A synthetic executive deck may be both `AIWorkslop`, `ManagementSlop` and `PresentationSlop`. A human-written city-page matrix may be both `HumanSlop`, `SEOSlop` and `DoorwayPageSlop`.

## Work Slop

### Established AI Workslop

BetterUp Labs and the Stanford Social Media Lab define workslop as AI-generated workplace content that looks polished but lacks substance and leaves colleagues to perform the real thinking and cleanup. Their 2025 survey reported that 40% of US desk workers had received it in the prior month and estimated roughly two hours of resolution effort per incident.

The ontology preserves this narrow meaning as `AIWorkslop`. It does **not** silently redefine the established term.

### Proposed Work Slop family

`WorkSlopFamily` is a neutral grouping concept. An artifact, activity or process becomes a candidate when:

- it has weak contribution to a legitimate work goal;
- it shifts material checking, interpretation, coordination or repair work to others;
- it presents as more complete, authoritative or useful than it is;
- it is delivered, mandated, repeated or scaled beyond a private rough-draft context.

Low quality alone is insufficient.

### Human Work Slop

`HumanWorkSlop` captures the same burden-transfer structure where humans are the primary source or maintainer. Examples include ritual reports copied from existing trackers, status documents with no audience-specific decision value, or recurring manual output created to satisfy an activity metric.

This class is not a scientific diagnosis and must not be used as a label for disliked colleagues. Classification should attach to a specific artifact, process or observed pattern, never to a person.

## Management Slop

Management Slop is the most important Human Work Slop subtype because management has authority to impose distribution and recurring cost.

Its research foundations are adjacent rather than slop-specific:

- **Organizational bullshit** research studies communication made with indifference to truth, including managerial commanding and strategizing.
- **Organizational bullshit perception** research identifies truth disregard, the boss and bullshit language as measurable factors.
- **Red tape** scholarship describes rules that consume organizational resources without contributing to legitimate goals.
- **Administrative burden** research decomposes imposed burden into learning, compliance and psychological costs.
- **Administrative bloat** models show how once-useful processes can become obsolete and continue consuming resources.
- **Meeting research** treats effectiveness as objective achievement and repeatedly identifies unclear goals and excessive meeting load as productivity problems.
- **Goodhart effects** show how a proxy loses validity once optimized as a target.

### Management subtypes

| Type | Core failure | Strong signals |
|---|---|---|
| `StrategySlop` | Direction without choices | no trade-offs, resources, testable assumptions or priorities |
| `JargonSlop` | Impressive language without operational meaning | undefined buzzwords, strategic ambiguity, authority by tone |
| `MeetingSlop` | Synchronous cost without justified objective achievement | no objective, wrong attendees, status reading, no decision or owner |
| `DecisionSlop` | Performance of decisiveness without accountable commitment | no criteria, evidence, owner, constraints or decision log |
| `MetricsSlop` | Proxy optimization replaces the underlying goal | vanity metrics, activity quotas, dashboard proliferation, gaming |
| `ProcessSlop` | Obsolete or duplicated workflow persists | no owner, no sunset, duplicate approvals, ritual reporting |
| `AdministrativeSlop` | Learning, compliance or psychological cost is disproportionate | repeated evidence requests, opaque forms, burden shifted outward |
| `ComplianceSlop` | Proof of control replaces risk reduction | checkbox evidence, duplicated attestations, audit theater |

### Management Slop exclusions

The following are not sufficient evidence:

- a manager made an unpopular decision;
- a process is slow or inconvenient;
- a control creates work;
- a meeting is long;
- a strategy contains uncertainty;
- a metric is imperfect.

Safety, security, legal, accessibility, audit and separation-of-duties controls can be burdensome and still legitimate. A Slop classification needs evidence of disproportionality, weak goal contribution and burden transfer.

## SEO Slop

SEO Slop is defined as search-facing content or site structure whose primary function is ranking or answer-engine visibility while offering little original value to users.

The category is generation-neutral. Google’s spam policy explicitly states that scaled content abuse can be created with generative AI, scraping, transformations, stitching or other means; the decisive issue is manipulation and low value.

### SEO subtypes

| Type | Official-policy anchor | Operational boundary |
|---|---|---|
| `ScaledContentSlop` | Scaled content abuse | many low-value or unoriginal pages created to manipulate ranking |
| `DoorwayPageSlop` | Doorway abuse | near-duplicate query or regional pages funnel users elsewhere |
| `SiteReputationSlop` | Site reputation abuse | detached third-party content borrows host ranking signals |
| `ExpiredDomainSlop` | Expired domain abuse | inherited authority is repurposed for low-value ranking content |
| `ScrapedRemixSlop` | Scraping / scaled content abuse | copied, stitched, translated or synonymized material without added value |
| `SearchSaturationSlop` | Scaled content / network behavior | coordinated clusters occupy result space or simulate corroboration |
| `GEOManipulationSlop` | Search manipulation including generative responses | content is engineered to be cited or repeated by answer systems rather than to inform users |

SEO work is not Slop merely because it targets queries, uses structured data, contains affiliate links or is produced programmatically. Useful, original, transparent content remains outside the class.

## Additional evidence-backed types

### OpenSourceContributionSlop

Two 2026 research programs describe low-quality AI-generated code, pull requests, issues, documentation and bug reports as externalizing review costs onto maintainers. One large study frames the effect as AI-DDoS and reports lower merge rates for one-time contributors relative to a counterfactual. This supports a distinct `OpenSourceContributionSlop` class with review-capacity harms.

### Hiring Slop

Current reporting uses “hiring slop” for bulk, AI-optimized applications that reduce candidate signal and create screening overload. The label is marked **emerging**, not established, because robust independent measurement is still limited.

### Educational Slop

A peer-reviewed 2025 mixed-methods study explicitly operationalized slop in biomedical educational videos and identified hazards to learners and teachers. This justifies an `EducationalSlop` class rather than treating education as only a distribution channel.

### Slopaganda

A 2026 academic paper proposes `Slopaganda` for high-volume AI-generated ideological noise that manipulates attention through semantic saturation, context collapse and cognitive exhaustion. It differs from ordinary disinformation because the mechanism can be flooding rather than persuasion by a single false claim.

## Candidates not promoted to stable classes

Several useful phrases remain in the candidate registry:

- `CustomerServiceSlop`: generic responses that shift resolution work to customers;
- `DataSlop`: too broad without a sharper boundary from ordinary data-quality defects;
- `DashboardSlop`: currently covered by `MetricsSlop`;
- `PodcastSlop`: currently a medium-specific instance of Audio Slop;
- `GamblingSlop`: usually an instance of Site Reputation or Affiliate/SEO abuse;
- `LocalNewsSlop`: overlaps Article Slop, impersonation and expired-domain abuse;
- `FinancialAdviceSlop` and `MedicalAdviceSlop`: high-harm domains, but evidence is not yet sufficient for broad stable classes.

Keeping these as candidates prevents uncontrolled ontology growth.

## Cross-cutting dimensions

The extension adds eleven reusable dimensions:

1. `goal_contribution_deficit`
2. `recipient_effort_transfer`
3. `superficial_competence`
4. `actionability_deficit`
5. `verification_deficit`
6. `coordination_overhead`
7. `process_obsolescence`
8. `metric_gaming`
9. `distribution_manipulation`
10. `scale_repetition`
11. `truth_indifference`

They supplement rather than replace the core AI Slop dimensions.

## False-positive safeguards

Human and workplace classification is socially riskier than content classification. The following safeguards are mandatory:

1. Classify artifacts, activities and systems—not personalities.
2. Require observable burden or outcome evidence, not aesthetic dislike.
3. Separate generation mode from form and harm.
4. Preserve legitimate controls, accessibility work and safety repetition.
5. Treat drafts, brainstorming and requested ideation as context-sensitive.
6. Do not infer AI generation from polished or generic style alone.
7. Record counter-evidence and the intended legitimate goal.
8. Use `candidate` rather than `confirmed` where organizational value is disputed.
9. Avoid using Slop labels as retaliation or performance-management shortcuts.
10. Reassess processes over time; something once useful can become obsolete, and something apparently redundant can retain resilience value.

## Suggested scoring profile

Use the core ontology’s noisy-OR evidence aggregation. For workplace cases, prioritize:

| Dimension | Default severity when strongly evidenced |
|---|---|
| Recipient effort transfer | high |
| Goal contribution deficit | high |
| Truth indifference | high |
| Verification deficit | high in high-risk domains |
| Actionability deficit | medium |
| Coordination overhead | medium |
| Process obsolescence | medium |
| Metric gaming | medium to high |
| Superficial competence | medium |
| Scale repetition | medium |

A candidate should normally require at least one high-severity signal plus two independent medium signals. Confirmation should require documented recipient burden, repeated occurrence or measurable system impact.

## Sources

1. BetterUp Labs & Stanford Social Media Lab. *Workslop: The Hidden Cost of AI-Generated Busywork* (2025).
2. Shaib et al. *Measuring AI “Slop” in Text* (2025), arXiv:2509.19163.
3. Kommers et al. *Why Slop Matters* (2026), arXiv:2601.06060.
4. Google Search Central. *Spam Policies for Google Web Search*, updated 2026-05-19.
5. Christensen, Kärreman & Rasche. *Bullshit and Organization Studies* (2019), Organization Studies 40(10).
6. Ferreira et al. *This Place Is Full of It: Towards an Organizational Bullshit Perception Scale* (2022).
7. Spicer. *Shooting the shit: The role of bullshit in organisations* (2013).
8. Campbell, Pandey & Arnessen. *A Meta-Narrative Review of the Red Tape and Administrative Burden Literatures* (2022).
9. Moynihan, Herd & Harvey. *Administrative Burden: Learning, Psychological, and Compliance Costs* (2015).
10. Microsoft. *Work Trend Index: Will AI Fix Work?* (2023).
11. Yang & Grenier. *What Leads to Administrative Bloat?* (2024), arXiv:2412.15378.
12. Tankelevitch et al. *Nudging Attention to Workplace Meeting Goals* (2026), arXiv:2602.16939.
13. Afroz et al. *AI Slop is DDoSing Open Source* (2026), arXiv:2607.04003.
14. Baltes, Cheong & Treude. *An Endless Stream of AI Slop* (2026), arXiv:2603.27249.
15. Jones et al. *AI-Generated “Slop” in Online Biomedical Science Educational Videos* (2025), JMIR Medical Education 11:e80084.
16. Edwards. *The résumé is dying, and AI is holding the smoking gun* (2025), Ars Technica.
17. Bortoș. *Slopaganda: How AI-Generated Noise Is Reconfiguring the Digital Infosphere* (2026).
18. Fire & Guestrin. *Over-Optimization of Academic Publishing Metrics* (2019), arXiv:1809.07841.
19. Ghia et al. *Will AI Agents Free Us From Meaningless Work?* (2026), arXiv:2606.12430.
20. Miklian & Katsos. *“That’s AI Slop, You Bot!”* (2026), arXiv:2606.12073.

The machine-readable source registry with URLs and type mappings is in `human_work_seo_slop.json`.
