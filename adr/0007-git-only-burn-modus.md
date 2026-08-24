# 7. Git-only-Burn-Modus bei API-Ausfall

- **Status:** accepted
- **Datum:** 2026-08-25 (rückdokumentiert; Praxisfall, Burn-Log D001)

## Context and Problem Statement

Während des Issue-Burns fiel die GitHub REST API mit 401 aus (Token ungültig, ~22:58, 2026-08-24), während git-Push über den credential-helper weiter funktionierte. Die Queue sollte trotzdem durchlaufen (Stefan: „Schmeiss den issue burner an um alles zu burnen … Dokumentiere alles", D001/D004).

## Decision Drivers

- Kontinuität: qualitätsgeführte Arbeit darf nicht an einem Infrastruktur-Ausfall sterben.
- Review-/Gate-Disziplin bleibt vollständig erhalten (D005).
- Rückverfolgbarkeit: Branch → Issue muss ohne GitHub-PR-Metadaten rekonstruierbar sein.

## Considered Options

### Option 1: Burn pausieren, bis Token wieder geht
- Gut: kein Metadaten-Rückstau.
- Schlecht: Queue blockiert unbestimmte Zeit; menschlicher Eingriff nötig — widerspricht „Ich möchte nix manuell machen" (D005).

### Option 2: Git-only-Modus — Branch + TDD + Tests + Push wie gehabt; PR-Erstellung und Issue-Kommentare parken; Branch-Namenskonvention issue-N-slug + Burn-Log führt Branch→Issue-Register
- Gut: Arbeit läuft weiter mit vollen Gates; Rekonstruktion über Burn-Log; PRs/Issue-Links beim Token-Repair stapelbar.
- Schlecht: offene Branches ohne PR sind temporär unsichtbar für GitHub-Nutzer; geparkte Close-Kommentare müssen nachgepflegt werden.

## Decision Outcome

**Chosen option: Option 2.** Git-only-Burn-Modus gemäß D001: volle TDD-/Review-/Drift-Disziplin, Branches gepusht, PRs geparkt; Batch-Reports (burn-batch-X.md) + Burn-Log sichern Rückverfolgbarkeit.

## Consequences

- **Positiv:** Batches A–E liefen ohne Unterbrechung; jede Qualitätsschleife blieb intakt.
- **Negativ:** Nach Token-Repair ist ein Nachpflege-Burst nötig (PRs anlegen, Issue-Referenzen ergänzen).
- **Neutral:** D006-Daemon (Cron) feuert automatisch, sobald die API wieder 200 liefert.

## Confirmation

- Burn-Log führt Branch→Issue je Batch; Review-Protokolle je Batch (review-batch-X.md) dokumentieren die unabhängige Review-Pflicht trotz fehlender GitHub-PRs.

## More Information

- Issues: — (Prozessentscheidung)
- Burn-Log-Entscheidungen D001–D012: `research/slop-ontology-gap-2026-08-24/burn-log.md` (externe Quelle, dort konsultiert — hier zitiert, nicht kopiert)
