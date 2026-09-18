# ADR-0031: Hard Rule — Detector-Only (kein aktives Verbessern)

- **Status:** accepted
- **Datum:** 2026-09-18 (Entscheidung Stefan Hiecker, bindend)

## Context

**Entscheidung (Stefan Hiecker, 18.09.2026, bindend):** Dieses Repository
detektiert und kategorisiert Slop. Es verbessert nicht aktiv.

1. Write-side-Anleitungen (Schreibregeln, Authoring-Regeln, Style-Prompts)
   gehoeren NICHT in dieses Repo. Sie leben in
   MakerCologne/btm-skill-pipelines/write-side-rules.
2. Write-side-Evals (Prevention Contract ueber Generierungsvarianten) leben
   ebendort; dieses Repo traegt nur Detektions-Evals.
3. Kein Rewrite im Repo: deslop_loop_cli bleibt audit-only ohne mitgelieferten
   Fixer (ADR-0001 unveraendert gueltig).
4. Ausnahmen beduerfen eines neuen ADR mit Begruendung des Betreibers.

**Zusatz-Ruling (Stefan, 18.09., gleichrangig):** Aktive Slop-Entfernung ist
ein komplett eigener Skill, der die Ontologie integriert (als Abhaengigkeit),
nie Bestandteil dieses Repos. Dementsprechend sind zudem ausgelagert:
deslop_loop (Orchestrator), confirm (Signal-Bestaetigung vor Fixes),
voice_drift, run_audit (Loop-Run-Audit), fixer/ (Fix-Strategien),
deslop_loop_cli + Demo, die zugehoerigen Tests sowie editing-doctrine.md und
edit-self-check.md (Fix-Doktrin). Neues Zuhause:
MakerCologne/openclaw-skills/slop-removal (integriert die Ontology).
Zurueckbleibt als Detektion: alle Signale, der Scorer, Klassifikator,
Control-Sets, Detektions-Evals, human-voice.md (Counter-Profil fuer
keep_when-Bewertungen — Detektions-Referenz).

**Grund (Consequences):** Die Markt-Positionierung des Projekts ist Detector-Nische
(README); Praeventions-Inhalte im Detektor-Repo verwischen die Grenze und
kompromittieren die Unparteilichkeit des Detektors gegenueber den Regeln,
gegen die er misst. Folge: Der Detektor bleibt audit-only; aktive Entfernung
liegt beim externen Skill und kann sich unabhängig weiterentwickeln.

## Decision

## Considered Options

### Option 1: Status quo — Write-side-Inhalte im Detektor-Repo belassen
- Gut: keine Migrationskosten, Evals laufen weiter.
- Schlecht: Unparteilichkeit des Detektors leidet (er misst gegen Regeln, die er selbst mitliefert); verwischt die Detector-Nische.

### Option 2: Detector-Only-Hard-Rule mit Auslagerung nach btm-skill-pipelines/write-side-rules und eigenem Skill (gewählt)
- Gut: klare Trennung Detektion vs. Aktives Eingreifen; Detektor bleibt unparteiisch; eigener Skill kann die Ontologie als Abhängigkeit integrieren.
- Schlecht: Migrationsaufwand; externe Abhängigkeit für aktive Entfernung.

### Option 3: Aktives Deslop als Modus im Detektor-CLI (--fix)
- Gut: ein Tool für alles.
- Schlecht: widerspricht ADR-0001 (audit-only), Neutralität nicht haltbar; abgelehnt.

**Umsetzung:** Entfernung von authoring-rules.md, writing-rules.md,
test_writing_rules_docs.py, test_prevention_contract.py sowie der
write-side-Eval-Artefakte; Ueberfuehrung nach btm-skill-pipelines.
Betroffen aber VOR der Regel gemerged und damit zur Entscheidung gestellt
(Betreiber-Ruling ausstehend): references/editing-doctrine.md,
references/edit-self-check.md (PR #30, 11.09.), references/human-voice.md
(#21, 25.08., Counter-Profil).

Siehe Burn-Log: `research/slop-ontology-gap-2026-08-24/burn-log.md`.
