# Human Voice — positives Gegenprofil (Issue #21)

**Status:** redaktionelle Referenz (bearbeitbar) · **Quelle:** poteto/noodle
`unslop` — Abschnitt „Adding soul" (skills.sh/poteto/noodle/unslop, 2026-08-24,
Recherche: deep/06-poteto-recherche.md §3) plus Code-Soul aus brianlovin
`simplify` (deep/07-brianlovin-deslop.md §3.1, bl-I4).

Die Ontology ist rein detektivisch: sie sagt, was Slop *ist*, aber nicht,
wie guter Text *klingt*. „Removal ist nur half the job — sterile, voiceless
writing is just as obvious." Diese Referenz beschreibt den Zielzustand.
Sie ändert **keinen Scorer** — sie ist Redaktionsgegenstück zur Detektion.

Die sechs Prinzipien (je Beschreibung, Vorher/Nachher, Wann nicht):

### 1. Specific over generic

**Beschreibung:** Nicht „this is concerning", sondern „there's something
unsettling about agents churning away at 3am". Das Konkrete (Zeit, Ort,
Gerät, Name) ist die Stimme; das Abstrakte ist der Slop-Fall.

**Vorher:** „The deployment process has some concerning aspects."
**Nachher:** „The deploy hung for 40 minutes on Tuesday because the lock
on `staging.lock` was never released."

**Wann nicht:** Zusammenfassungen, Überschriften, Test-Beschreibungen —
dort ist die Abstraktion der Zweck. Auch juristische/formelle Prosa
(Genre-Profile, #42) verträgt weniger Konkretion.

### 2. Verbs over nouns (Abstraktion abbauen)

**Beschreibung:** Nominalisierungen verstecken Handlungen
(„the utilization of leverage for the achievement of alignment").
Verben tragen die Aussage: „we aligned by reusing".

**Vorher:** „The implementation of the optimization was performed."
**Nachher:** „We optimized it."

**Wann nicht:** Fachterminologie mit feststehenden Nomina
(Fachsprache-Exemtionen analog FU-3: „realizes a gain" bleibt). Namen
von Dingen sind keine Nominalisierungen.

### 3. Risks and flaws nennen

**Beschreibung:** „Acknowledge complexity. 'Impressive but also kind of
unsettling' beats 'impressive'." Wer nur lobt, klingt wie Marketing.
Echte Bewertungen enthalten Einwände, Kompromisse, Misserfolge
(„mistakes were made along the way" — als erlebte Wahrheit, nicht als
Slop-Formel).

**Vorher:** „The framework is powerful and elegant."
**Nachher:** „The framework is powerful; we still lost two nights to its
retry loop, and the docs don't mention it."

**Wann nicht:** Sachberichte ohne Bewertungsauftrag (News-Genre);
Zusage-Dokumente. Ein erzwungenes „aber" pro Satz ist die gleiche Formel
in gespiegelt — Risiko gehört zur Aussage, nicht zum Muster.

### 4. Genuine opinion

**Beschreibung:** „Have opinions. React to facts instead of neutrally
listing pros and cons." Erstes Person zulassen („Use 'I' when it fits.
First person isn't unprofessional."), Stellung beziehen, begründen.

**Vorher:** „There are arguments for both approaches."
**Nachher:** „I'd take the boring one: it failed once in two years, the
clever one failed twice last month."

**Wann nicht:** neutrale Vergleichstabellen, Gutachten mit
Interessenkonflikt-Regeln, redaktionelle Objektivitätsstandards. Und:
Meinung ohne Begründung ist nur lauter Slop.

### 5. Numbers and names statt Behauptungen

**Beschreibung:** „Be specific." Zahlen, Namen, Versionen, Commits,
Datenpunkte statt Adjektiv-Behauptungen. „Fast" ist eine Behauptung,
„cold start 1.2s → 0.4s" ist eine Aussage. (Korrespondiert zur Detektion
von fabricated-proof-metrics, #34: Zahlen müssen belegbar sein — nie
Zahlen erfinden, um konkret zu wirken.)

**Vorher:** „The new release is significantly faster and more robust."
**Nachher:** „v2.1 cut p99 latency from 890ms to 310ms (benchmark run
2026-08-24, eval/run_benchmark.py)."

**Wann nicht:** Wenn die Zahl nicht existiert: ehrlich unpräzise bleiben
(„roughly twice as fast in our setup") statt eine Precision-Maske
aufzusetzen — eine erfundene Zahl ist schlimmer als eine vage.

### 6. Sentence-length variation — gezielt

**Beschreibung:** „Vary rhythm. Short sentences. Then longer ones that
take their time. Mix it up." Uniforme Satzlänge ist ein Struktur-Signal
(burstiness), Variation ist lebendig — aber gezielt, nicht als tick:
Ein-Drei-Wort-Sätze als Stilmittel sparsam, nicht als Takt.

**Vorher:** „The system is fast. The system is stable. The system is
easy to use. The system is well documented."
**Nachher:** „It's fast. More surprising: it stayed fast under the load
test we ran on Friday, with all twelve workers hammering the same
endpoint."

**Wann nicht:** technische Schritt-für-Schritt-Anweisungen, Kochrezepte,
Prüfprotokolle — dort ist Uniformität Korrektheit, nicht Slop
(Genre-Guards). „Let some mess in" heißt kontrollierte Unvollkommenheit
in Meinungsprosa, nicht schlampige Anleitungen.

## Code-Soul-Defaults (bl-I4, brianlovin `simplify`)

Positive Stil-Defaults fürs Code-Editing — Empfehlungen, nicht nur Verbote:

- **Benannte Funktionen** statt anonymer Blöcke: ein Name ist Doku;
  `def _retry_with_backoff()` erklärt, ein geschachtelter Closure nicht.
- **Frühe Returns** statt verschachtelter Bedingungen: flache Pfade,
  Guard-Klauseln zuerst („avoid nested ternary operators",
  „choose clarity over brevity").
- **Löschen statt Auskommentieren**: toter Code ist Git-Gedächtnis-Müll —
  gelöschte Zeilen leben im History; auskommentierte leben in jedem
  Review. Auch: „removing unnecessary comments that describe obvious
  code".
- „Never change what the code does — only how it does it" (Preserve
  Functionality ist harte Grenze jeden Nachschreibens).

**Wann nicht:** Hotfixes unter Zeitdruck, generierter/wachsender Code,
der erst stabil laufen muss. Code-Soul ist zweite Stufe nach deslop,
nicht_parallel dazu (deslop → simplify, bl-I5).

## Kombination mit Detektion — Abgrenzungsregeln

### Kollision mit #24 (Adverb-Rate)

Die Adverb-Rate (#24) zählt `-ly`-Wörter (> 4 % auf ≥ 40 Wörtern;
Intensifier wie *very/really/extremely* amplifizieren). Human Voice
empfiehl aber u. a. „genuinely hard", „kind of unsettling" — legale
menschliche Verstärkung. Abgrenzung:

1. **Informations tragende Adverbien bleiben:** „genuinely hard" sagt
   etwas über den Grad der Ehrlichkeit; „remarkably innovative" sagt
   nichts. Schreibe das erstere, meide das letztere.
2. **Höchstens ein Intensifier pro Absatz.** Stacked intensifiers
   („really very quite unique") sind Slop unabhängig von der Stimme.
3. **Starkes Verb schlägt Adverb+Verb:** „slammed" statt „hit hard",
   „botched" statt „badly failed" — senkt zugleich die #24-Rate.
4. Richtung des Konflikts: Die Detektion gewinnt als Gate (Score bleibt
   maßgeblich); Human Voice gewinnt bei der Wahl *welcher* zugelassene
   Ausdruck. Ein Text, der nur die Rate unter 4 % hält, aber sonst
   formelhaft bleibt, ist trotzdem Slop — und umgekehrt ist eine ehrliche
   Stimme mit 5 % `-ly` kein Automatik-False-Positive: #24 ist
   bedingter Beitrag, kein Eigen-Trigger (never fires on its own).

### Weitere Grenzen

- **Burstiness (#Dimension):** Prinzip 6 *unterstützt* die Metrik —
  Variation senkt den AI-Verdacht; kein Zielkonflikt.
- **Genre-Profile (#42):** In formalen Genres (legal, academic) gelten
  die Prinzipien 1/4/6 abgeschwächt — Genre-Exemptions gehen vor.
- **Selbst-Audit (poteto Schritt 4):** Nach dem Edit einmal lesen:
  „Was macht das noch offensichtlich generiert?" — eine Iteration, dann
  Schluss.

---

*Diese Datei ist bearbeitbare Referenz, kein Scorer-Input. Änderungen
hier haben keine Score-Wirkung; Tests (tests/test_human_voice.py) pinnen
nur Struktur: 6 Prinzipien mit Vorher/Nachher und Wann-nicht, Code-Soul,
#24-Abgrenzung, SKILL.md-Verlinkung.*
