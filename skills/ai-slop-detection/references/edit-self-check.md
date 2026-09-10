# Edit Self-Check — Prüfung nach jedem Fix (Issue #30, Teil 2)

**Status:** redaktionelle Referenz (bearbeitbar) · **Quellen:**
no-ai-slop eval.md (31 Checks), stop-slop (5 Dimensionen),
research/slop-loop-pipeline-2026-08-24/ (LOOP-I5, Review-Zweitpass
mit introduced_signals-Tracking), humanizer-de (Evidence-Ledger).
Regeln des Edits selbst: `references/editing-doctrine.md` (Teil 1).

Dieser Check läuft als **Skill-Schritt 4b** nach jedem Fix, bevor das
Ergebnis ausgegeben wird. Er ersetzt kein Re-Scoring — er prüft das,
was der Scorer nicht sieht: Fakten, Voice, neue selbstgemachte Signale.

## Re-Check-Loop (Review-Zweitpass)

„Did my fix create new slop?" — Der Re-Check misst
**introduced_signals**: Signale, die NACH dem Fix triggern, aber NICHT
vorher triggerten. Diese sind Fix-Artefakte und werden anders behandelt
als persistierende Altsignale:

- introduced_signal → Fix überarbeiten (nicht drüberdeslopen), Ursache
  ist der Edit selbst
- persistierendes Signal nach 2 Fix-Runden → lassen oder ESCALATE
  (siehe Abbruchkriterium, editing-doctrine.md; Termination-Semantik
  #62: nie „success" durch Erschöpfung)

## ~20 Checks

**A. Faktenebene (Evidence-Gate, BLOCK bei Fail):**
1. Keine Zahl im Nachher, die nicht im Vorher stand (oder belegt ist)
2. Kein Name/Zitat/DOI hinzugefügt oder entfernt
3. Keine Kausalität neu behauptet („deshalb", „führt zu")
4. Keine Abschwächung von Autoritätsgraden („belegt"→„vermutlich")
5. Keine Verstärkung von Autoritätsgraden
6. Kürzungen explizit markiert (nicht stillschweigend)

**B. Voice-Non-Regression (BLOCK bei klarer Drift):**
7. Lieblingswörter des Autors nicht durch Synonyme ersetzt
8. Satzlängen-Rhythmus erhalten (kein Split/Merge ohne Signal-Anlass)
9. Bluntness erhalten (keine Ton-Sanitisierung)
10. Humor/Ironie nicht geglättet
11. Register erhalten (formell bleibt formell, locker bleibt locker)
12. Ergebnis klingt nicht „zu sauber" (Naturalness-Guard #74/#81)

**C. Minimum-Effective-Edit (Fail → Fix verkleinern):**
13. Nur Signal-Hits adressiert (keine Nebenarbeiten)
14. Kleinste Edit-Einheit gewählt (Wort < Satz < Absatz)
15. Kein Streichbad (proportional zur Signaldichte)
16. Keine „weil ich eh dabei bin"-Umformulierungen

**D. Neue Signale (introduced_signals, Fail → Edit-Loop):**
17. Re-Scan: keine Signale, die nur im Nachher-Text triggern
18. Keine menschliche Slop-Fußnote („Ich habe das umgeschrieben,
    damit es menschlicher klingt")
19. Keine Deslop-Vokabular-Lecks („delve", „tapestry" etc. durch
    andere Slop-Wörter ersetzt, statt durch schlichte Sprache)

**E. Transparenz (Output-Format):**
20. What-changed-Report erstellt (Template unten), 1–3 Sätze

## What-changed-Output-Template

```
Fixed: <Signal-ID(s)> in <Position/Anzahl>
Edits: <n> kleinste Änderungen (Wort/Satz), keine Fakten berührt
New signals introduced: 0 (Re-Scan clean) | <Liste, Loop läuft>
Uncertain: <was unklar blieb / ESCALATE-Grund>
```

Zweistufiges Cleanup-Habit: erst **deslop** (Signale entfernen nach
Doctrine), dann bewerten ob **simplify** (Struktur straffen) überhaupt
nötig ist — simplify ist ein zweiter, getrennter Schritt mit eigenem
Self-Check, kein Doppel-Edit in einem Durchgang.

## Abbruch / Fertigstellung

- Fertig: Ziel-Signale weg, introduced_signals = 0, Checks A–B grün,
  Report vorhanden
- Abbruch (ESCALATE): Loop konvergiert nicht in ≤ 3 Durchläufen,
  Evidence-Gate blockiert wiederholt, oder Voice-Drift nicht
  behebbar → „human review required" + run report
  (Termination-Semantik: docs/loop-guards/62-…, #62)
