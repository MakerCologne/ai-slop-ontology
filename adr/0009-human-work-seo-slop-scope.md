# 9. Geltungsbereich: Menschlich verfasster Work-/SEO-Slop (Portierung #86)

- **Status:** proposed (decision-needed — burn-borne, Issue #86 DoD-Punkt 1; Freigabe analog adr/0008)
- **Datum:** 2026-09-12
- **Issues:** #86 (dieses ADR + Portierung), verwandt adr/0008 (#90, #89), adr/0001, adr/0006

## Metadaten

```yaml
status: proposed
date: 2026-09-12
decision-makers: [ ]
consulted: [ ]
informed: [ ]
```

## Context and Problem Statement

PR #6 (Head `87f264f`) enthielt eine vollständige `extensions/human-work-seo-slop/` — WorkSlop (Output, der Arbeit auf den Empfänger verschiebt), SEO-Slop und die Abgrenzung `HumanAuthoredWorkSlop` (menschlich verfasst, gleiche Struktureigenschaften). Die PRs #4/#6 sind nicht mergebar (keine gemeinsame Historie), der Inhalt soll über #86 portiert werden. Dafür ist zuerst die Geltungsbereichs-Frage zu entscheiden: **Fällt menschlich verfasster Slop in den Geltungsbereich dieser Ontologie?**

adr/0008 (proposed) beantwortet dieselbe Frage bereits für ideologischen Human Slop mit „Slop ist ein Risikoprofil, keine Autorschaftsklasse“. Dieses ADR wendet denselben Satz auf Arbeits- und Distributionskontexte an — kein neuer Sachverhalt, nur ein neuer Anwendungsfall des bereits begründeten Prinzips.

## Decision Drivers

- adr/0001: Detector, kein Rewriter — Autorschaft ist kein Urteil über Qualität oder Absicht.
- adr/0006: neue Module default detect-only.
- adr/0002: `ontology.json` ist SSOT; Extension darf keinen zweiten Wahrheitsstand eröffnen.
- adr/0008 (proposed): Human Slop = Risikoprofil (Goal-Defizit, Verifikationsdefizit, Push), nicht Autorschaft.
- Signal-DoD Punkt 3: score-wirksame Signale brauchen SSOT-Eintrag — Extensions ohne Score-Beitrag umgehen das bis zur Beförderung.

## Considered Options

### Option 1 — Out-of-scope: nur AI-Workslop portieren, Human-Anteil verwerfen
- Gut: kein neuer konzeptioneller Ballast; „Slop“ bleibt synonym mit KI-Anteil.
- Schlecht: widerspricht adr/0008-Begründung (Risikoprofil); SEO-Slop ist ohnehin generationsneutral (Ranking-Manipulation durch menschliche Content Farms ist das Original-Phänomen); der Schaden des Empfängers hängt nicht vom Autor ab.

### Option 2 — In-scope, detect-only (Extension als `nursery`, kein Score-Beitrag)
- Gut: deckt Work-/SEO-Slop mit 11 dimensionalen Definitionen ab, ohne den Scorer zu verbiegen; `AIWorkslop` bleibt etabliert und AI-gebunden, `HumanWorkSlop` bleibt klar abgegrenzt (Regeln kollabieren die Generierungsmodi nicht — testen die portierten Tests explizit); reversibel; konsistent mit adr/0006/0008.
- Schlecht: Struktur-Extension ohne Korpus-Evidenz — Status `grounded_extension`/`candidate` ist eine Behauptung aus angrenzender Forschung, nicht aus eigenem Benchmark.

### Option 3 — In-scope mit Score-Beitrag
- Gut: sofort messbar.
- Schlecht: Signal-DoD nicht erfüllt (keine Fixtures, kein FP-Benchmark auf dem Hard-Negative-Korpus); verletzt Sequencing-Disziplin (DoD-Punkt 7).

## Decision Outcome

**Chosen option: Option 2 (In-scope, detect-only), weil** die Geltungsfrage durch adr/0008 präjudiziert ist (Risikoprofil, nicht Autorschaft) und Option 2 der einzige Weg ist, der Portierungsinhalt sofort zu sichern, ohne Score- oder Korpusdisziplin (adr/0003, #0005, Signal-DoD) zu verletzen.

## Consequences

- **Positiv:** WorkSlop/SEOSlop-Klassen mit 11 dimensionalen Definitionen verfügbar; Quellenregister mit Online-Verifikation (`verify_sources.py --online`, Coverage-Gate `--min-verified`, CI-Workflow wöchentlich); Defekt aus PR #6 („no dead links“ bei Totalausfall) bleibt gefixt.
- **Negativ:** Extensions sind `nursery`/`experimental` — keine score-wirksamen Signale, bis Signal-DoD 3/3/2 erfüllt und ADR accepted.
- **Neutral/Follow-ups:** Beförderung einzelner Klassen in `ontology.json`-SSOT (DoD-Punkt 2 volle Parität) erst nach Korpus-Evidenz; #87 (Playground-Adapter) kann erst danach den Katalog generieren.

## Confirmation (Compliance-Prüfung)

- `tests/test_human_work_seo_extension.py`: Statuswerte, Parent-/Source-Resolution, FP-Exclusions pro Typ, Nicht-Kollaps von Human/AI-Generierung, SEOSlop-Generationsneutralität.
- `tests/test_parity_human_work_seo.py` (neu): TTL/JSON-Parität der Extension-Klassen (DoD-Punkt 2, detect-only-Niveau).
- `python3 extensions/human-work-seo-slop/verify_sources.py` (offline, strukturell) in CI-Testsuite.
- Kein Import in `src/`-Scorer → kein Score-Beitrag (detect-only per Konstruktion).

## More Information

- Quelldateien: Branch `claude/ontology-update-extend-7kn6h3`, Head `87f264f` (PR #6).
- Schwestersache: `adr/0008-human-ideological-slop-scope.md` (ideologischer Human Slop).
