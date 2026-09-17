# Terminierungs-Semantik: Fixpoint ≠ Optimum (#62)

**Status:** spec · **Verwandt:** #59 (Trajectory-Guard), #47 (Quartals-Drift), SCORE-GOVERNANCE.md · **Quellen:** Krishna et al., arXiv:2303.13408 (Paraphrase-Detektion versagt jenseits beobachteter Trigger); Loop-Design Herleitung (b)–(e), Report-Abschnitt (f)

## Kernaussage

Ein Loop, der `maxIter` erreicht, terminiert **nie** als Erfolg. Der Fixpoint eines Fix-/Review-Loops ist ein lokales Optimum relativ zum Detektor-Maßstab der Ontology v1.x — nicht eine Garantie über Slop-Freiheit im Allgemeinen. Wer beides gleichsetzt, optimiert den Detektor statt die Qualität (Goodhart, vgl. M9).

## Terminierungs-Zustände (Zustandsmaschine M7)

Der EXIT-CHECK des Loops (`DETECT→TRIAGE→FIX→VERIFY→EXIT-CHECK`) kennt genau zwei terminale Zustände:

| Zustand | Bedingung | Ausgabe-Formulierung |
|---|---|---|
| **OUTPUT** | Score < Schwellwert **und** alle Guards grün **und** Voice-Non-Regression bestanden | „slop-frei nach Maßstab der Ontology v1.x (Stand <Datum>)" |
| **ESCALATE** | maxIter erreicht, Guard-Anomalie (#59), Rollback-Kette, oder ungelöste Hard-Gate-Verletzung (#55) | „human review required" + Run-Report (`runs/<runId>/`, #61) |

Es gibt keinen dritten Zustand „maxIter erreicht, sieht gut aus → OUTPUT". Genau das ist das Anti-Pattern des weichen maxIter-Passthroughs: die Iterationsgrenze wird zum Qualitätsurteil umgedeutet.

## Warum die Garantie maßstabsgebunden ist

Der Scorer sieht nur die Signale der Ontology v1.x. Paraphrasiertes Slop, das keine getriggerte Signale mehr matcht, ist für den Detektor unsichtbar — nicht verschwunden (Krishna et al., arXiv:2303.13408: Paraphrase-Angriffe umgehen auch trainierte Detektoren mit hoher Rate). Daher:

- Die Ausgabe-Garantie lautet immer relativ: „nach Maßstab der Ontology v1.x, Signalstand <Datum/Commit>", nie absolut „KI-ferenzfrei".
- Ein Score von 0.00 ist ein Messwert des Detektors, keine Eigenschaft des Textes. Plötzliche Perfekt-Scores sind sogar ein Evasions-Signal (#59, Trigger 1).

## Anti-Pattern-Liste

1. **Weiches maxIter-Passthrough:** „6 Iterationen durch, Score 0.05 — passt" ohne ESCALATE-Markierung. Iterationsgrenze ≠ Qualitätsgate.
2. **Absolute Output-Formulierung:** „Der Text ist jetzt slop-frei" ohne Maßstabs-Bindung (Ontology-Version + Datum).
3. **Score als alleiniges Exit-Kriterium:** Score-Threshold ohne Guardrails (Voice-Drift #56, Trajektorie #59, Bestätigung #58) — ein Rewriter kann den Detektor optimieren statt die Qualität.
4. **Stillsuccess bei Anomalie:** Guard-Rot (Evasions-Verdacht, Rollback-Kette) wird im Report erwähnt, der Lauf aber dennoch als OUTPUT klassifiziert.
5. **Unversionierte Garantie:** Output-Zusicherung ohne Ontology-Stand — unvergleichbar mit späteren Re-Scores (#47) und nicht reproduzierbar (M6).

## Umsetzung

- Loop-Runner MUSS am maxIter-Abbruch `verdict: escalate` setzen und den Run-Report verlinken; STILLER Erfolg ist ein Testfehler.
- Output-Text MUSS die Formulierung aus der Tabelle tragen (maßstabsgebunden bei OUTPUT, `human review required` bei ESCALATE).
- Review-Checks für Loop-PRs prüfen die Terminal-Zustands-Klassifikation mit (`tests/`-Seite, s. DoD #64).
