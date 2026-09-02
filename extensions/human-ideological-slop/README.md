# Extension: Human / Ideological Slop

**Status:** nursery · **ADR:** adr/0008 (proposed, #90) · **Issues:** #93 (dieses Dokument), #94 (Ethnopluralismus), Epic #89, verwandt #86

Schwesterklasse zu `SyntheticContent` — ohne dessen drei AI-Bedingungen zu verbiegen. Grundatz (adr/0008): **Slop ist ein Risikoprofil, keine Autorschaftsklasse.**

## Klassenhierarchie

```
ContentItem
├── SyntheticContent → AI_SlopCandidate → ConfirmedAI_Slop
└── HumanSlopCandidate → ConfirmedHumanSlop
        ├── IdeologicalSlop
        ├── PolemicSlop
        ├── MoralPanicSlop
        └── PuritySlop
```

## Bedingungen Human Slop (Entwurf)

1. Primärquelle Mensch oder Organisation (oder Hybrid mit menschlichem Frame)
2. `hasHumanOversightLevel = ritual_reproduction` (Frame seit n Zyklen unverändert)
3. Push-Distribution
4. `hasInformationGain ≈ 0` (IU1/IU2)
5. `hasFalsifiability = low`

Zusätzliche Intent-Werte: `identity_signaling`, `enemy_construction`, `mobilization`.

## Abgrenzung zu #86

#86 = WorkSlop / SEOSlop / HumanAuthoredWorkSlop (Struktur von Arbeits- und SEO-Texten). Diese Extension = Ideologie / Polemik / Panik. Die gemeinsame Superklasse `HumanSlopCandidate` ist erlaubt; Dimensionen werden nicht gemischt.

## Scoring-Regel

`polemic_risk` wird **nicht** in `slop_score` gefaltet (Noisy-OR würde Political Copy mit SEO-Slop verrechnen). Routing:

- `polemic_risk` allein → named evidence, kein RAG-Ausschluss
- `polemic_risk` + Harm `Democracy Risk` + Entmenschlichung → `CriticalReviewRequired`

## Dateien

| Datei | Inhalt |
|---|---|
| `human_ideological_slop.json` | Klassen, Bedingungen, Intents (JSON-LD-Stil wie ontology.json) |
| `human_ideological_slop.ttl` | TTL-Parity |
| `examples.json` | je Subtyp 2 positiv, 2 Hard-Negative (Kurzskelette, `source: own:handwritten`) |
| `RESEARCH.md` | Analyse Ethnopluralismus als Strategie (#94) + Genealogie |

## Definition of Done (Status)

- [x] ADR-Ja (teilumfänglich: B-Default, A nach Opt-in — adr/0008 proposed)
- [x] YAML/JSON/TTL-Parity — Lexikon-Einträge `lexikon/entries/human-slop.yaml` und `ideological-slop.yaml` (nursery)
- [x] Lexikon-Einträge mit `claims[]` + Quelle (Schema-Pflicht)
- [x] Beispiele: je Subtyp 2 positiv, 2 Hard-Negative (Kurzskelette)
- [x] Kein Signal score-wirksam ohne eigenes Signal-Issue + 3/3/2
