# DOC-STYLE.md — Schreibregel für die eigene Doku

**Status:** verbindlich für jedes Markdown-Dokument in diesem Repo · **Gate:** `scripts/self_check_docs.py` (Issue #48) · **Bezug:** #23 (Quote-Exemption), #69 (Markdown-Präpass), docs/SCORE-GOVERNANCE.md

Ein Detektor, dessen eigene Doku die eigenen Signale auslöst, ist ein angreifbares Narrativ. Diese Datei sagt, wie hier geschrieben wird, damit das Gate grün bleibt — und wann eine Ausnahme legitim ist.

---

## Die Regel

**Zitiertes Material gehört in Markup, eigene Aussagen in Fließtext.**

Der Präpass (#69) entfernt vor dem Scoring genau das, was Markup als Zitat ausweist: Code-Fences, Inline-Code, Blockquotes, Tabellen, Zitat-Listen und das Inhaltsverzeichnis. Was in Fließtext steht, wird als eigene Stimme gewertet — zu Recht.

Praktisch heißt das:

- Ein Beispiel-Slop-Satz steht in einer Fence oder einem Blockquote, nie als Absatz.
- Ein Signalname oder eine Phrase steht als `code span`, nicht nackt im Satz.
- Eine Aufzählung von Katalog-Einträgen benutzt Anführungszeichen oder Backticks je Eintrag — dann erkennt der Präpass sie als Katalog und nicht als Argumentation.
- Eine Prosa-Liste (Argumente, Gründe, Schritte) bleibt bewusst stehen und wird gewertet. Das ist gewollt: Argumente sind eigene Stimme.

## Was das Gate prüft

`scripts/self_check_docs.py` bewertet jedes Markdown im Repo nach dem Präpass und schlägt fehl, sobald ein Dokument die Entscheidungsschwelle 0.40 erreicht. Der Lauf ist ein CI-Schritt und kein Bericht.

```console
$ python scripts/self_check_docs.py
```

## Ausnahmen

Manche Dokumente **müssen** Katalogmaterial im Fließtext führen: ein Changelog, der die neu aufgenommenen Phrasen benennt; ein Review, der die gefundenen Buzzwords zitiert. Sie in Markup zu zwingen würde die Aussage verfälschen, nicht den Stil verbessern.

Solche Dokumente stehen in `eval/self_check_docs.json` — mit **Begründung** und einer **Obergrenze, die am gemessenen Wert klebt**. Die Form ist dieselbe wie bei `eval/fp_baseline.json`, und die Disziplin auch:

- Ohne Begründung kein Eintrag (Test).
- Die Obergrenze darf höchstens 0.10 über dem gemessenen Wert liegen — sonst ist sie eine Blankoerlaubnis statt einer Ratsche (Test).
- Wird ein registriertes Dokument schlechter, schlägt das Gate trotzdem fehl.
- Wird es sauber, verliert es den Eintrag (Test).

Ein Eintrag ist eine dokumentierte Schuld, keine Erledigung.

## Was ausdrücklich nicht erlaubt ist

**Umformulieren, damit das Gate schweigt.** Wenn ein Signal in eigener Prosa feuert, sind zwei Antworten richtig — die Prosa ist tatsächlich schlecht und wird besser, oder das Signal ist an dieser Stelle falsch und bekommt ein Ticket. Den eigenen Satz so lange zu drehen, bis der Detektor ihn nicht mehr sieht, ist die Goodhart-Bewegung, vor der docs/SCORE-GOVERNANCE.md warnt: die Metrik wird zum Ziel, und gemessen wird nichts mehr.

Wo so etwas doch passiert ist, gehört es offengelegt — siehe die Offenlegung in #88 zu einer Formulierungsänderung in `docs/USER-GUIDE.md`.
