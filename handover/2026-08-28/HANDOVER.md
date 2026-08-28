# Handover — ai-slop-ontology, Stand 2026-08-28

**Für:** einen Agenten mit Schreibrecht auf Repo und GitHub
**Repo:** https://github.com/MakerCologne/ai-slop-ontology
**Übergebener Stand:** Version 2.8.0 (`master` nach PR #105) — Hash mit `git log --oneline -1` prüfen, nicht raten
**Vorgängersessions:** Triage, drei P0-Fixes, fünf P1-Fixes, vier PRs gemergt (#99 → 2.6.0, #101 → 2.6.1, #103 → 2.7.0, #105 → 2.8.0), zwei alte PRs geschlossen (#4, #6)

---

## 0. Auftrag in einem Satz

Arbeite den priorisierten Rückstand ab — **P0 zuerst, dann P1** — nach den Regeln in `CONVENTIONS.md`, und dokumentiere jeden Schritt im zugehörigen Issue. Die Qualitätserwartung des Auftraggebers ist wörtlich: *„alles weiter so in Issues dokumentiert".*

## 1. Das Erste, was du tun musst

**Lies `PITFALLS.md`, bevor du irgendetwas anfasst.** Darin stehen neun Fallen, jede mit Beleg. Zwei haben Gates gebaut, die nicht fehlschlagen konnten — in einem Repo, dessen ganzer Zweck ehrliche Messung ist. Drei weitere (7–9) sind teurer: dort waren die Tests grün und hatten recht, sie prüften nur die falsche Frage, und die falsche Zahl war schon veröffentlicht.

Wenn du nur eine Zeile mitnimmst, dann diese: **eine neu gemessene Zahl geht nicht in einen PR-Body, bevor du einen Weg gesucht hast, sie zu widerlegen.**

**Dann:** `bash scripts/verify.sh` gegen einen frischen Checkout. Wenn das nicht durchläuft, ist der übergebene Stand nicht der, den du bekommen hast, und alles Weitere steht auf Sand.

## 2. Der Blocker, den du nicht allein lösen kannst

**#100 (P0): GitHub Actions ist deaktiviert.**

```
$ gh workflow run tests.yml --ref master
failed to run workflow: Cannot trigger a 'workflow_dispatch' on a disabled workflow
```

Seit dem 25.08. läuft kein CI. Der letzte Lauf, der stattfand, war rot (Läufe 150–163, immer `ModuleNotFoundError: No module named 'pytest'`). Die Ursache ist mit #99 behoben; die **Deaktivierung** braucht einen Menschen im Actions-Tab oder `PUT /repos/MakerCologne/ai-slop-ontology/actions/workflows/{id}/enable`. Die MCP-Werkzeuge dieser Umgebung kennen kein `enable` — siehe `ACCESS.md`.

**Konsequenz für dich:** Solange das so ist, sind alle „grün"-Aussagen lokal. Sag das in jedem PR dazu, so wie ich es getan habe. Behaupte nie CI-Grün, das du nicht gesehen hast.

**Erste Handlung deiner Session:** prüfe, ob der Workflow inzwischen aktiv ist. Wenn ja, starte einen Lauf auf `master` und schließe #100 mit dem Ergebnis. Wenn nein, erinnere den Auftraggeber einmal daran — nicht jede Session neu.

## 3. Reihenfolge

```
#100  (P0, braucht Menschen)
  │
  ├─ Defekt-Strang (P1):  #106 → #107 → #70 → #52 → #46 → #47 → #55 → #56
  │                       (#88 und #85 sind erledigt)
  │
  └─ Vorhaben-Strang:     #92 → #90 → #94 → #98      (Epic #89, Human/Ideological Slop)
                          #91 ist die Entscheidungsvorlage für #90
```

Die beiden Stränge konkurrieren. Der Auftraggeber hat den Defekt-Strang gewählt („P1 defect strang", 2026-08-28) — halte dich daran, bis er etwas anderes sagt. Innerhalb der Stränge ist die Reihenfolge begründet (`BACKLOG.md`).

**#106 und #107 hängen zusammen und kommen zuerst.** Beide stammen aus dem Review von #85, beide betreffen dieselbe Zahl, und beide sind Fragen der Art „was misst diese Messung eigentlich". #106 braucht den Multi-Start-Optimierer, den #85 mitgebracht hat; #107 braucht eine Entscheidung über den Evaluationskorpus und berührt damit adr/0005 — das ist die einzige Stelle im aktuellen Rückstand, an der du wahrscheinlich eine ADR schreiben musst.

## 4. Was du nicht tun sollst

- **Kein Rewriter für politische Texte.** adr/0001 und das Human-Slop-Paket schließen das aus. Der Detektor benennt, er korrigiert nicht.
- **Keine Umformulierung, bis der Detektor schweigt.** `docs/DOC-STYLE.md` verbietet das ausdrücklich. Wenn ein Signal in eigener Prosa feuert, ist entweder die Prosa schlecht oder das Signal falsch — beides bekommt eine Antwort, keine Wortwahl-Ausweichbewegung. (Wo mir das doch passiert ist, steht es offengelegt in #88.)
- **Keine Default-Änderung am Scoring** ohne Re-Baseline nach `docs/SCORE-GOVERNANCE.md`. Der Markdown-Präpass ist deshalb opt-in.
- **Kein Signal ohne Signal-DoD 3/3/2** und ohne Eintrag in `ontology.json`.
- **Keine CC-BY-SA-Pattern-Übernahme** aus humanizer-de oder anderen Fremdkatalogen. Eigene Re-Derivation mit Attribution (Lizenzregel aus #76).
- **PR #4 und #6 nicht wiederbeleben.** Sie haben keine gemeinsame Historie mit `master` (`git merge-base -a` leer). Ihr Inhalt ist als #86/#87 ticketiert.
- **Keine Zahl aus `--cross-validate` als „Generalisierungsschätzer" bezeichnen.** Sie ist held out mit Bezug auf die **Gewichte**; die Signalinventare stammen aus demselben Korpus (#107). Der Vorbehalt steht in der Ausgabe selbst und ist per Test gepinnt — nimm ihn nicht heraus, solange #107 offen ist.

## 5. Definition of Done je Ticket

Ein Ticket ist fertig, wenn **alle** fünf Punkte stehen:

1. RED-Commit mit fehlschlagendem Test, GREEN-Commit mit dem Fix. Beide Hashes im Issue-Kommentar.
2. `bash scripts/verify.sh` grün — alle acht Gates, nicht nur die Suite.
3. Bei Score-Wirkung: Change-Protokoll vorher/nachher über `eval/corpus.jsonl`, mit expliziter Aussage, ob ein Hard Negative sich bewegt hat.
4. Neue Testdatei in `docs/EVALS.md` auf L1/L2/L3 abgebildet — `check_methodology` erzwingt das und schlägt sonst fehl.
5. Issue-Kommentar mit DoD-Abgleich Punkt für Punkt, dann schließen.

Und einer, der nach #85 dazugehört:

6. **Bei jeder neu gemessenen Zahl:** benenne, wogegen sie gemessen ist und was sie nicht sagt. Wenn zwei Zahlen gleich sind, die sich unterscheiden sollten, ist das ein Befund. Wenn eine Suche nichts findet, ist das kein Beweis, dass es nichts gibt — konstruiere den Gegenbeleg, bevor du folgerst.

## 6. Dateien in diesem Paket

| Datei | Zweck |
|---|---|
| `HANDOVER.md` | du bist hier |
| `STATE.md` | verifizierter Stand von `master`, mit den Zahlen und wie man sie nachmisst |
| `BACKLOG.md` | jedes offene Ticket mit Einstiegspunkt und Einschätzung |
| `CONVENTIONS.md` | die Regeln des Repos, die ein Agent kennen muss |
| `ACCESS.md` | was die Umgebung kann und was nicht — inklusive der Dinge, die fehlgeschlagen sind |
| `PITFALLS.md` | sechs Fallen aus der Vorgängersession, mit Beleg |
| `scripts/verify.sh` | alle acht Gates in der Reihenfolge des CI-Workflows |

## 7. Ton

Der Auftraggeber arbeitet knapp und erwartet Substanz. Was in der Vorgängersession funktioniert hat:

- Befunde **reproduzieren**, bevor man sie meldet. Jedes P0-Issue in diesem Repo trägt ein Reproduktionskommando.
- Eigene Fehler benennen, statt sie stillschweigend zu korrigieren. Die Offenlegung in #88 und der Review-Nacharbeit-Abschnitt im CHANGELOG sind Beispiele.
- Unterscheiden zwischen *behoben*, *ticketiert* und *nicht angefasst* — und nie das zweite als das erste ausgeben.
- Nicht jede Zwischenfrage stellen. Fragen, wenn zwei Lesarten zu materiell verschiedener Arbeit führen; sonst entscheiden und die Annahme benennen.
- **Reviews ernst nehmen und die Korrektur sichtbar machen.** In #85 haben zwei unabhängige Reviews (der eigene `/code-review` und Codex) je einen Fehler gefunden, der die Kernzahl des PRs ungültig machte. Beide Male stand die Korrektur als eigener Kommentar im PR und die falsche Fassung blieb stehen, statt überschrieben zu werden. Das kostet nichts und ist der Grund, warum die Zahlen in diesem Repo überhaupt etwas wert sind.
