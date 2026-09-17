# Terminierungs-Semantik: Fixpoint ≠ Optimum (#62)


**Status:** normativ · **Geltungsbereich:** jeder DESLOP-Loop-Run (`src/deslop_loop.py`, #51) und jede Aussage über Loop-Output · **Quellen:** research/slop-loop-pipeline-2026-08-24/report.md Abschnitt (f) (externes Research, Herleitung ebd. Abschnitt (b)–(e)); Krishna et al., arXiv:2303.13408 (Paraphrase-/Entfernungs-Robustheit)

## 1. Kernaussage

Ein Loop-Terminierungszustand ist **keine** Aussage über die Qualität des Textes, sondern über den **Maßstab des Detektors**. Der Fixpoint (keine weiteren bestätigten Signale im Detektor-Score) ist nicht das Optimum (bestmöglicher menschlicher Text). Der Scorer sieht paraphrasierten Slop jenseits seiner Trigger nicht (Krishna et al., arXiv:2303.13408). Deshalb sind alle Output-Garantien **maßstabsgebunden**.

## 2. Terminierungs-Semantik: OUTPUT vs. ESCALATE

| Verdict | Auslöser (Exit-Check) | Bedeutung | Erlaubte Formulierung |
|---|---|---|---|
| `EXIT_OK` | E1 ∧ E2 ∧ E4 (am Top-of-Iteration-DETECT) | Alle bestätigten Signale unterhalb der Schwellen; keine kritischen Hard-Gate-Signale; keine neu inkubierten Signale | „slop-frei **nach Maßstab der AI Slop Ontology v\<version\>**“ |
| `EXIT_ESCALATE` | E3 (Stagnation: 2 akzeptierte Iterationen mit Δ < ε) | Fixpoint oberhalb des Schwellwerts erreicht — ehrliches Eingeständnis, dass der Fix endet, obwohl Signale bleiben | „human review required“ |
| `EXIT_ESCALATE` | E5 (`maxIter` erreicht) | Budget erschöpft — **nie** still als Erfolg durchgehen | „human review required“ |
| `EXIT_ESCALATE` | E4-Verletzung / NO_FIX / NO_CANDIDATE | Fixes inkubieren neue Signale oder kein Fix verfügbar | „human review required“ |

`EXIT_OK` erfordert **alle drei** Checks E1, E2 **und** E4 gleichzeitig; E3 und E5 sind **immer** ESCALATE-Terminals. Es gibt keinen Weg, per maxIter still zum OUTPUT zu kommen.

## 3. Formulierungsregeln

**Erlaubt (maßstabsgebunden, versioniert):**
- „slop-frei nach Maßstab der AI Slop Ontology v2.9.0“
- „keine bestätigten Signale über Schwellenwert X des Scorer-Satzes v\<version\>“
- „ESCALATE: human review required (E5: maxIter)“

**Verboten (absolute Garantien):**
- „Text ist jetzt sauber / menschlich / optimal“
- „Kein AI-Slop mehr enthalten“
- „Erfolgreich bereinigt“ ohne Verdict-Angabe

Jede Aussage, die aus einem Loop-Run abgeleitet wird, muss den Verdict (`EXIT_OK`/`EXIT_ESCALATE`) **und** die Detektor-Version (aus `runs/<runId>/manifest.json`) tragen.

## 4. Anti-Pattern-Liste

1. **Weiches maxIter-Passthrough:** „maxIter erreicht, Score aber schon viel besser → als Erfolg werten“. Verboten — E5 ist per Definition ESCALATE. Score-Verbesserung ist kein Ersatz für Schwellen-Erfüllung.
2. **Absolute Output-Garantie:** „slop-frei“ ohne Maßstabs- und Versionsbindung. Der Scorer erkennt paraphrasierten Slop jenseits seiner Trigger nicht.
3. **Stiller Erfolg:** Loop-Ende ohne Verdict im Report/Audit. `result.json` ohne `verdict`-Feld ist ein Defekt.
4. **Fixpoint = Optimum-Gleichsetzung:** „Der Loop terminiert im Optimum.“ Falsch — der Fixpoint ist detektorspezifisch; ein anderer Scorer kann am selben Text noch Signale finden.
5. **Score-Verfall kaschieren:** Δ-Score-Stagnation als „konvergiert“ statt als E3-ESCALATE melden.
6. **Versionssprung stillschweigend:** Garantie mit Detektor v2.x ausgesprochen, nachgelagert mit v2.y verifiziert — Garantien gelten pro Version (Re-Score nötig).

## 5. Durchsetzung

- Implementiert in `src/deslop_loop.py` (E1–E5, Verdict-Enum `EXIT_OK | EXIT_ESCALATE`, kein Silent-Success-Pfad).
- Audit-Pflicht: `runs/<runId>/result.json` führt Verdict + maßstabsgebundene Garantie-Formel (Konzept #61).
- L1-Tests der Exit-Checks (13 Tests, deterministische Fake-Detektoren/Fixer) sichern ab, dass E3/E5 nie als `EXIT_OK` durchgehen.
- Verwandt: #51 (Loop-Runner), #61 (Run-Audit-Format), #58 (Signal-Bestätigung), #59 (Trajectory-Monitoring als Evasions-Gegenmaßnahme).

## 6. Ergänzungen aus der Spec (Zustandsmaschine M7)

Der EXIT-CHECK des Loops (`DETECT→TRIAGE→FIX→VERIFY→EXIT-Check`) ist als Zustandsmaschine M7 mit genau zwei terminalen Zuständen (OUTPUT / ESCALATE) definiert; es gibt keinen dritten Zustand „maxIter erreicht, sieht gut aus → OUTPUT“.

### Warum die Garantie maßstabsgebunden ist

Der Scorer sieht nur die Signale der Ontology v1.x. Paraphrasiertes Slop, das keine getriggerte Signale mehr matcht, ist für den Detektor unsichtbar — nicht verschwunden (Krishna et al., arXiv:2303.13408: Paraphrase-Angriffe umgehen auch trainierte Detektoren mit hoher Rate). Daher:

- Die Ausgabe-Garantie lautet immer relativ: „nach Maßstab der Ontology v1.x, Signalstand <Datum/Commit>“, nie absolut „KI-ferenzfrei“.
- Ein Score von 0.00 ist ein Messwert des Detektors, keine Eigenschaft des Textes. Plötzliche Perfekt-Scores sind sogar ein Evasions-Signal (#59, Trigger 1).
- Wer Fixpoint und Optimum gleichsetzt, optimiert den Detektor statt die Qualität (Goodhart, vgl. M9).
- Output-Zusicherungen ohne Ontology-Stand sind unvergleichbar mit späteren Re-Scores (#47) und nicht reproduzierbar (M6); Score-Threshold allein (ohne Voice-Drift #56, Trajektorie #59, Bestätigung #58) ist kein zulässiges Exit-Kriterium.

### Umsetzung (Review/DoD)

- Review-Checks für Loop-PRs prüfen die Terminal-Zustands-Klassifikation mit (`tests/`-Seite, s. DoD #64).
- Verwandt: #59 (Trajectory-Guard), #47 (Quartals-Drift), SCORE-GOVERNANCE.md.
