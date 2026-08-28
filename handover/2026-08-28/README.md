# Übergabepaket — ai-slop-ontology, 2026-08-28

Für einen Agenten mit Schreibrecht auf Repo und GitHub.

**Zielrepo:** https://github.com/MakerCologne/ai-slop-ontology
**Übergebener Stand:** v2.8.0 (`master` nach PR #105), 656 Tests grün
**Lizenz des Repos:** CC BY 4.0

## Inhalt

| Datei | Zweck |
|---|---|
| `HANDOVER.md` | der Arbeitsauftrag — hier anfangen |
| `PITFALLS.md` | neun Fallen aus den Vorgängersessions, jede mit Beleg — **vor** der ersten Änderung lesen |
| `STATE.md` | verifizierter Stand mit den Zahlen und den Kommandos, die sie nachmessen |
| `BACKLOG.md` | offene Issues, priorisiert, je mit Einstiegspunkt |
| `CONVENTIONS.md` | die Regeln des Repos — TDD-Form, Score-Governance, Signal-DoD, was automatisch erzwungen wird |
| `ACCESS.md` | was die Umgebung kann und was nicht, inklusive der Fehlschläge |
| `scripts/verify.sh` | alle acht Gates in der Reihenfolge des CI-Workflows |

## Reihenfolge

1. `HANDOVER.md` lesen
2. `PITFALLS.md` lesen — das ist der Teil, der Zeit spart. Die Fallen 7–9 sind die teuersten: dort waren die Tests grün und hatten recht, sie prüften nur die falsche Frage.
3. Repo klonen, `pip install pytest hatchling pyyaml`
4. `bash scripts/verify.sh` aus der Repo-Wurzel. Erwartung: `ALLE GATES GRUEN`
5. Prüfen, ob der tests-Workflow inzwischen aktiv ist (#100)
6. `BACKLOG.md`, dann arbeiten

`scripts/verify.sh` liegt auch im Repo unter demselben Pfad — die Kopie hier ist für den Fall, dass du das Paket vor dem Checkout liest.

## Was in dieser Session passiert ist

Triage aller offenen Issues mit neuem P0/P1-Schema (#54), zwei nicht mergebare Alt-PRs geschlossen (#4, #6), drei P0- und fünf P1-Defekte behoben und über vier PRs gemergt (#99 → v2.6.0, #101 → v2.6.1, #103 → v2.7.0, #105 → v2.8.0), das Human-Slop-Übergabepaket als Epic #89 mit acht Unterissues angelegt.

Aus dem Review von #85 sind zwei neue P1 entstanden (#106, #107) — beide betreffen die Frage, was die Benchmark-Zahl eigentlich misst. Sie stehen im Rückstand ganz vorn.

## Was nicht passiert ist

**GitHub Actions ist deaktiviert** und ließ sich mit den Rechten dieser Session nicht wieder einschalten (#100). Seit dem 25.08. läuft kein CI; der letzte Lauf war rot. Alle „grün"-Aussagen der Vorgängersession sind lokal nachgefahren und in den PRs als solche ausgewiesen.

Vom Human-Slop-Strang (#89–#98) ist **nur die Ticketierung** erledigt, keine Implementierung. Der Auftraggeber hat den Defekt-Strang vorgezogen.
