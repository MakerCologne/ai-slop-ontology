# Loop-Guard: #111 — metadata-slop Verhaltens-/Struktur-Signale

**Issue:** [#111](https://github.com/MakerCologne/ai-slop-ontology/issues/111) —
Signal] metadata-slop: PR-/Commit-Metadaten als neue Signalklasse (blind-spot A7, BS-I6)
**Datum:** 2026-09-12 · **Modus:** detect-only (ADR-0001/0006) · **Branch:** `burn/issue-111-metadata-slop`

## Was umgesetzt wurde

Erweiterung von `src/metadata_slop.py` (bestehend seit #45) um drei
regelbasierte, empirisch kalibrierte Analyzser-Gruppen. Jede Gruppe ist
FP-guarded: mindestens 2 unabhängige Regeln müssen feuern (anti-slop
`max-failures`-Mechanik, vgl. #117 Gates-Prinzip).

| Signal | Quelle (kalibriert) | Regeln | Input |
|---|---|---|---|
| `CommitVelocitySlop` | TryCadence/Cadence | >100 additions/min sustained; ≥3 aufeinanderfolgende Gaps <60s (Burst); add/delete >90% bei Volumen >200 Zeilen; Ratio-Spread <0.02 über ≥4 Commits | `list[CommitRecord]` (timestamp, additions, deletions) |
| `PRStructureSlop` | peakoss/anti-slop | ≥2 Emoji im Titel; geblockter Marketing-Term im Titel; Code-Referenzen (Backticks/Paths) ohne Diff-Bezug; >200 Zeichen + Agent-Keywords | `dict(title, body, changed_files)` |
| `CommitKeywordSlop` | drhiidden/gitorit | Agent-Vokabular (enhancing/seamlessly/comprehensive/…) **UND** Struktur (>200 Zeichen ODER Bullet-Gerund-Liste) | `str` Message |

Design-Entscheidungen:

- **Strukturierte Inputs, kein Text-Scraping**: Velocity braucht Commit-Metadaten,
  PR-Struktur braucht changed_files — beides Absicht: Dangling-Ref-Prüfung ist
  nur mit Diff-Kontext möglich (genau der anti-slop-Punkt: „Code-Referenzen
  ohne echten Diff-Bezug").
- **Einzelwort ist kein Slop**: `CommitKeywordSlop` feuert nur bei
  Keyword+Struktur-Kombination — „robust" in einer ehrlichen 60-Zeichen-Message
  bleibt sauber (Negativ-Fixtures decken das ab).
- **SSOT**: `ontology.json` `signals.metadata.indicators` um die drei
  Signale erweitert (Beschreibungen inkl. Kalibrierungsquelle + FP-Guard);
  check_ssot grün (C1–C4).
- Classifier-Fassade: `classify_commit_history()`, `classify_pull_request()`
  als Convenience-Pass-throughs auf `MetadataSlopClassifier`.

## Bewusste Lücken (Folgearbeit)

- Kein Git-Backend: Analyzser arbeiten auf Datenstrukturen, das Einsammeln
  (`git log`-Parsing / GH-API) ist bewusst nicht Teil dieses Issues
  (detektionsseitige Regel-Spezifikation, wie im Issue gefordert).
- Zeitfenster-gestaffelte Velocity (pro Stunde statt Gesamt-Spanne) nicht
  umgesetzt — Gesamt-Spanne ist die konservativere Variante.
- Kein Auto-Close / keine Benachrichtigung an PR-Autoren: detect-only,
  nie interventionistisch (ADR-0006).

## Tests

`tests/test_metadata_slop_111.py` — 14 Tests: pro Signalgruppe Positiv-,
Negativ- und explizite FP-Guard-Fixtures (Einzel-Regel-Hit bleibt stumm),
plus Classifier-Integration. Suite gesamt grün.
