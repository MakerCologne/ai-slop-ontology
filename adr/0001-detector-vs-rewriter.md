# 1. Rewriter-vs-Detector-Positionierung

- **Status:** accepted
- **Datum:** 2026-08-25 (rückdokumentiert; Konflikt offen seit #30/#38)
- **Decision-Makers:** Stefan / BTM.one, Burn-Prozess

## Context and Problem Statement

#30 plante einen Edit/Rewrite-Modus (aktive Textverbesserung), #38 verlangte „Detector, kein Rewriter". Der offene Zielkonflikt blockierte Roadmap-Entscheidungen (#54): Darf dieses Repo Texte aktiv umschreiben oder nur detektieren?

## Decision Drivers

- Goodhart-Risiko: Ein Rewriter im selben System kann den Detektor optimieren statt die Textqualität (#59, Loop-Research (d); Gao et al. 2210.10760).
- Klare Verantwortung: Detektion = reproduzierbar, CI-fähig, versioniert (M8 Determinismus-vor-LLM).
- Rewriter-Anforderungen (Minimum-Effective-Edit, Voice-Budget β=25%, #56/#60) brauchen eigene Evals und Guardrails.

## Considered Options

### Option 1: Detector + integrierter Rewriter (Modus-Flag im Scorer)
- Gut: ein Artefakt, End-to-End-Workflow.
- Schlecht: Score-Selbstmanipulation möglich; jede Rewrite-Logik gefährdet die Detektor-Neutralität; untestbare Kopplung.

### Option 2: Detector-only im Repo; Rewrite als separates Skill/Repo
- Gut: Scorer bleibt neutral und deterministisch; Rewrite kann eigene Evals (Voice-Non-Regression) bekommen; Klare Scope-Grenzen.
- Schlecht: Integration-Aufwand für Konsumenten, die beides wollen.

## Decision Outcome

**Chosen option: Option 2 (Detector-only).** Das Repo liefert Detektion/Scoring; aktives Rewriting gehört in ein separates Skill mit eigenen Voice-Guardrails. Repair-Empfehlungen (Minimum-Effective-Edit-Hinweise, #30-Anteil) bleiben als *dokumentierte* Gegenmaßnahmen Teil der Ontologie — ohne Score-Pfad.

## Consequences

- **Positiv:** Scorer-Neutralität, Goodhart-Resistenz (M9), klare Verantwortungsgrenze; #38 vollständig umgesetzt.
- **Negativ:** Konsumenten mit Rewrite-Bedarf brauchen das separate Skill; #30 in diesem Repo auf Gegenmaßnahmen-Doku reduziert.
- **Neutral:** Rewriter-Skill muss die DoD #64-Anforderungen + Voice-Budgets erfüllen.

## Confirmation

- Review-Regel: PRs, die schreibende Transformationen in den Scorer-Pfad bringen, werden abgelehnt (Referenz: DoD #64, Governance #67).
- detect-only-Module-Disziplin: ADR-0006 / #9 (`code_slop.py` ist detect-only).

## More Information

- Issues: #30, #38, #54, #56, #59, #60
- Burn-Log-Entscheidungen (D001–D012): `research/slop-ontology-gap-2026-08-24/burn-log.md` (externe Quelle, hier zitieren, nicht kopieren)
- Loop-Research Goodhart-Kapitel: `research/slop-loop-pipeline-2026-08-24/report.md` (extern)
