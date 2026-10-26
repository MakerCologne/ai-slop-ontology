# DEPENDENCY-BOARD.md — depends-on-Relationen der offenen Issues

**Status:** verbindliche Roadmap-Referenz · **Quelle:** Issue #54 · **Letzter Abgleich:** 2026-10-06

Das Board deklariert die Abhängigkeiten zwischen offenen Issues, die bislang nur implizit in Issue-Bodies standen. Regeln: ein Issue mit offener `depends-on`-Voraussetzung wird nicht bearbeitet (SIGNAL-DoD Punkt 7, Sequencing-Disziplin); ADR-Entscheidungen haben Vorrang vor Roadmap-Notizen.

## Entscheidung #30 vs. #38 — erledigt

Der in #54 genannte Zielkonflikt „Rewriter vs. Detector-only" ist durch `adr/0001-detector-vs-rewriter.md` entschieden: **Detector-only** im Repo, Rewriting in separates Skill. #30 ist damit auf Gegenmaßnahmen-Doku reduziert und blockiert keine Roadmap-Entscheidung mehr. Der Decision-Record ist ADR-0001 selbst.

## Abhängigkeitsgraph (offene Issues)

Beziehungen als `Issue → hängt ab von`:

| Issue | depends-on | Grund (Beleg) |
|---|---|---|
| `#30` | `#56`, `#60` | Rewrite-Anforderungen brauchen Voice-Budgets + Best-of-N-Auswahl (ADR-0001, Consequences) |
| `#35` | `#12` | Domain-Trigger brauchen den Re-Kalibrierungs-Loop als Datengrundlage (BS-Notiz in #54: „#36/#35→#12") |
| `#36` | `#12` | Modell-Notizen/Halbwertszeiten sind nur mit laufender Empirie kalibrierbar (BS-Notiz in #54) |
| `#53` | Tokenizer-Refactor | Reihenfolge explizit in #53-Body: „NUR nach Tokenizer-Refactor (BS-I4)" |
| `#73` | — | DE-Layer baut auf bestehender Infrastruktur auf (#40/#43), keine Issue-Blocker |
| `#76` | `#73` | Master-Issue: Coverage-Mapping setzt den DE-Signallayer voraus (#76-Titel) |
| `#77` | `#73` | Vokabular-Erweiterung ist Teil des DE-Layers (#77 im DE-Pfad) |
| `#110` | `#77` | 4 Meta-Communicative Signale aus der Hassid-Liste erweitern die DE-Phrasendatenbank |
| `#86` | PR #6 | Portierung des Bestands aus PR #6 |
| `#87` | PR #6 | Portierung des Bestands aus PR #6 |
| `#90` | ~~—~~ | ADR-0008 ausgearbeitet (2026-09-02, PR #125), Status bleibt **proposed** — Abschluss nur nach Stefan-Freigabe (`status:decision-needed` bleibt bestehen) |
| `#91` | `#90` | Bewerteter Vorschlag (B zuerst, A danach) in ADR-0008 dokumentiert; DoD-Rest = Entscheidungs-Festschreibung im Epic #89, hängt an #90-Freigabe |
| `#92` | ~~`#90`~~ | **Umgesetzt + promoviert** (PR #127 nursery 09-02, PR #276 Promotion 09-23): `src/de_ideology.py`, 10 Patterns, detect-only per ADR-0006, FP=0 auf Hard-Negatives. Implementierung lief unter der B-Nursery-Ausnahme von #91 („B-Nursery explizit detect-only") |
| `#93` | `#90`, `#92` | Extension-Gerüst vorhanden (`extensions/human-ideological-slop/`: YAML/JSON/TTL + RESEARCH + examples); Mergen/Kern-Anbindung weiterhin erst nach #90-Freigabe |
| `#94` | ~~`#92`~~ | Analyse erarbeitet; DoD-PR #294 offen (Belege, RESEARCH, Lexikon-Verweis) |
| `#98` | `#92` ✅ | Eval-Korpus-Beschluss für die B-Klasse liegt vor (Basis der #92-Promotion); Korpus-Erweiterung siehe Corpus-v2-Plan |
| `#95`–`#97` | `#89` | Fallstudien hängen am Epic-Rahmen |
| `#55` | `#118` (schwach) | Severity-Tiers und Gates-Statt-Score adressieren dieselbe Achse; #118 definiert das Gate-Format |
| `#117` | `#55` (schwach) | Geometrisches Mittel gewichtet nach Severity-Tier |

Kritischer Pfad: `#12 → #35/#36`, `#53 → Sprach-Erweiterungen`, `#90 → #93/#98` (B-Schiene #92/#94 weitgehend umgesetzt, Rest hängt an Stefan-Freigabe von ADR-0008).

## Pflege

Änderungen am Board erfolgen im selben PR wie die zugehörige Issue-Bearbeitung. Neue Issues deklarieren Abhängigkeiten im `depends-on`-Feld des Templates #66; dieses Board ist die aggregierte Sicht.
