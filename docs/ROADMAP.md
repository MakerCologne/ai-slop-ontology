# Roadmap & Dependency-Board

> Issue #54 · Stand: 2026-09-09 · Upstream-of-diesem-Doc sind die GitHub-Labels: `P0`/`P1` als Label, alles Unbeschriftete ist P2 (Konvention der Triage 2026-08-28, korrigiert am 2026-08-29).

Dieses Dokument ist der gepflegte Ort für die zwei Dinge, die GitHub selbst nicht trägt:

1. **depends-on-Relationen** zwischen offenen Issues (GitHub kennt keine Issue-Relationen; Kommentar-Threads veralten).
2. **Den aktuellen Zustand des Boards** — die Triage vom 2026-08-28 lebt in Kommentarform unter #54 und ist seither veraltet.

## 1. Entscheidungs-Records (strategische Konflikte)

| Konflikt | Status | Record |
|---|---|---|
| #30 (Rewriter) vs. #38 (Detector-only) | **entschieden** | adr/0001 (Option 2, Detector-only, 2026-08-25). #38 umgesetzt via #151/#165; #30 ist in diesem Repo auf dokumentierte Gegenmaßnahmen reduziert — aktives Rewriting gehört in ein separates Skill mit eigenen Voice-Guardrails (#56, #60). |
| #90: Fällt ideologischer Human Slop in den Geltungsbereich? | **offen** (Label `status:decision-needed`) | adr/0008 existiert als Platzhalter; Entscheidungsvorlage ist #91 (Optionsbewertung A vs. B). #90 entscheidet auch den ADR-Anteil von #86. |

## 2. Board-Stand 2026-09-09

### Erledigt seit der Triage 2026-08-28

Die P0-Defekte und die P1-Defekt-Tickets sind geschlossen:

| Ticket | Art | Beleg |
|---|---|---|
| #82, #83, #69 | P0-Defekte | closed |
| #84, #85, #70, #48, #52, #88 | P1-Defekte/Gates | closed |
| #78, #79 | P1-Vorhaben | closed (anchor_diff, Null-Edit-Contract) |

### Offene P1 (Vorhaben, keine Defekte mehr)

| # | Sache | blockiert durch |
|---|---|---|
| #91 | Optionsbewertung A vs. B (Entscheidungsvorlage) | nichts — nächster sinnvoller Schritt |
| #90 | ADR ideologischer Slop | #91 (Vorlage), Anschauung aus #92 |
| #92 | detect-only DE-Rhetorik-Nursery | nichts (detect-only ist per adr/0006 default) |
| #94 | Ethnopluralismus-Lexikon | nichts (liefert #98) |
| #98 | Eval-Korpus Human/Ideological Slop | #90 (ADR-Ja), annotierte Texte aus #95/#96/#97 |
| #55 | Severity-Tier je Signal | — PR #179 offen |
| #56 | Voice-Drift-Guardrail | — |
| #46 | Signal-Kollisions-Matrix | — PR #181 offen |
| #47 | Kalibrierungs-Drift-Messvorschrift | Referenzkorpus (#72) liegt vor; hängt sachlich an #12 (Sampling-Harness) |
| #106 | Gewichts-Kalibrierung: Beitrag messen oder Anspruch zurücknehmen | — PRs #176/#177 offen |

### Offene PRs (Review-Queue)

| PR | für Issue | Stand |
|---|---|---|
| #172 | #36 model_notes | offen |
| #173 | #119 Findings-Receipts | offen |
| #174, #182 | #113 Mikro-Signale | offen |
| #175 | #35 triggered_by: domain | offen |
| #176, #177 | #106 Ablation/Gates | offen |
| #178 | #61 Run-Audit-Standard | offen |
| #179 | #55 Severity-SSOT | offen |
| #180 | #37 Human-Detection-Empirie | offen |
| #181 | #46 Kollisions-Matrix | offen |

#58 ist über PR #144 (merged 2026-09-02) umgesetzt; das Issue wartet auf Close. Ebenso faktisch erledigt über gemergte PRs: #11 (PR #169-Pendant im Merge-Zustand prüfen), #39 (#153), #71 (#159), #38 (#151/#165).

## 3. depends-on-Graph (offene Arbeit)

```
Human/Ideological-Slop-Strang (Epic #89):
  #92 B-Nursery ──────────┐
  #94 Ethnopluralismus ───┼──> #90 ADR ──> #93 A-Extension ──> #98 Eval-Korpus
                          │         └────> entscheidet ADR-Teil von #86
  #95/#96/#97 Fallstudien ┴───────────────────────┬──────────> #98 (annotierte Texte)
  #91 Optionsbewertung ──> #90 (Vorlage)

Portierung PR #6:
  #86 human/work/SEO-Extension ──> #87 Playground-Adapter
        └──> ADR-Teil hängt an #90

Kalibrierungs-Strang:
  #12 Sampling-Harness ──> #47 Drift-Messvorschrift
  #36 model_notes (PR #172) ──> #47 (Halbwertszeiten als Input)
  #116 reliability-/status-Schema ──> #118 Gates-für-Binärsignale, #117 geometrische Aggregation

Loop-/Fix-Strang:
  #46 Kollisions-Matrix (PR #181) ──> #56 Voice-Drift-Guardrail ──> #60 Best-of-N
  #55 Severity (PR #179) ──> Fix-Reihenfolge im Loop
  #61 Run-Audit (PR #178) ──> #59 Score-Trajectory-Monitoring
  #58 Signal-Bestätigung (done, #144)

Sprach-Strang:
  #76 DE-Pattern-Katalog (Master für #73) ──> #73 DE-Signallayer ──> #77 DE-Marker-Vokabular
  #73 ──> #53 ZH/JA/PT/IT/RU/AR/TR (zusätzlich blockiert durch Tokenizer-Refactor)

Neue Signale/Metriken (weitgehend unabhängig, P2):
  #110, #111, #112, #113, #114, #115, #121, #122, #124
  #119 Findings-Standard (PR #173) ──> #120 FP-Lern-Loop (Input-Standard)
  #121 Verification Ladder ──> #112 Gamed-Verification-Diff (Teilmenge)
```

## 4. Empfohlene Reihenfolge

1. **PR-Queue leeren** (#172–#182 reviewen/mergen) — danach schließen sich ~10 Issues von selbst.
2. **#91 → #90** — die einzige noch offene strategische Entscheidung; blockiert den gesamten Human-Slop-Strang (#93, #86/#87, #98) und damit 12+ Tickets.
3. **#47** — Referenzkorpus liegt vor, Messvorschrift fehlt; ohne sie altert der Korpus still (BS-WICHTIG).
4. Danach P2-Pool nach Strang-Abhängigkeit oben; #53 bleibt blockiert bis zum Tokenizer-Refactor.

## Pflege

- Update dieses Dokuments gehört zur Definition of Done jedes Issues, das Abhängigkeiten verändert (neu, geschlossen, um-priorisiert).
- Labels bleiben die Wahrheit für Priorität; dieses Dokument trägt nur die Relationen, die GitHub nicht abbilden kann.
