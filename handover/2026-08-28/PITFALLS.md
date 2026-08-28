# PITFALLS.md — neun Fallen aus den Vorgängersessions

Jede hier ist tatsächlich passiert, nicht ausgedacht. Sieben davon hat erst ein Review gefunden, nachdem „alle Gates grün" gemeldet war.

**1–6** stammen aus der Session vom Vormittag (#99, #101), **7–9** aus der Session am Nachmittag (#88, #85). Die drei neuen sind die teuersten: alle drei betreffen eine **Messung, die falsch war, obwohl sie plausibel aussah** — und in zwei Fällen hatte ich die Zahl bereits veröffentlicht.

---

## 1 · Ein Gate, das nicht fehlschlagen kann

**Was passierte.** Ich schrieb einen CI-Schritt, der die installierte CLI prüft:

```
slop score sample.txt
```

Ohne `--file` bewertet die CLI den **Dateinamen als Literal**. Ergebnis 0.00 statt 0.96 — der Schritt konnte nie rot werden. Dasselbe stand im zugehörigen Test. Beides fiel erst im Review auf, in einem PR, dessen Thema „Gates, die nicht laufen" war.

**Regel.** Nach jedem neuen Gate: **beweise, dass es fehlschlagen kann.** Schieb ihm etwas unter, das durchfallen muss, und sieh den roten Lauf. `tests/test_self_check_docs.py::test_a_slop_document_fails_the_gate` ist das Muster dafür.

---

## 2 · Eine Ratsche, die nicht ratscht

**Was passierte.** Ausnahmen im Self-Check-Register bekamen `max_score: 1.0` mit der Begründung „Deckel am Messwert". Classifier-Scores sind aber bei 1.0 gedeckelt und das Gate prüft `score <= budget` — die Obergrenze war unerreichbar. Die Dokumente hätten beliebig viel Slop aufnehmen können.

Mein eigener Test hat es nicht gemerkt, weil er den **Abstand** Deckel↔Messwert prüfte (1.0 − 0.973 = 0.027, unauffällig) statt der **Erreichbarkeit** des Deckels.

**Regel.** Bei jeder Schwelle: frag nicht „ist der Wert plausibel", sondern „**welche Eingabe verletzt sie**". Wenn du keine konstruieren kannst, ist die Schwelle Dekoration.

---

## 3 · Gerundete Zahlen im Vergleich

**Was passierte.** `run_benchmark.py` rundet Metriken auf drei Stellen für die Ausgabe. Die Untergrenzen `--min-precision/--min-recall` verglichen gegen diese gerundeten Werte. Ein Recall von 0.98999 wird als `0.990` gespeichert und rutscht durch `--min-recall 0.99`.

**Regel.** Runden ist Darstellung. Vergleiche laufen gegen den unrundeten Wert. Im Repo heißen die Felder jetzt `precision_exact` / `recall_exact` / `f1_exact`.

---

## 4 · Verkettete Regex-Durchläufe machen Entscheidungen instabil

**Was passierte.** Der Markdown-Präpass war eine Kette von Substitutionen über das ganze Dokument. Eine geleerte Tabellenzeile lässt die Folgezeile „nach Leerzeile" aussehen — der zweite Durchlauf urteilt anders. Ein Fuzz über 3.000 Fälle: **14 % nicht idempotent.**

Dazu drei Über-Entfernungen im selben Modul: ein `DOTALL`-Inline-Code-Regex löschte bei ungeradem Backtick alles bis zum nächsten (in `CHANGELOG.md` 28 Spannen, die größte 799 Zeichen); eine unterminierte Fence ohne abschließendes Newline wurde gar nicht entfernt; eingerückte Fortsetzungszeilen von Prosa-Listen galten als Codeblock.

**Regel.** Wenn Entscheidungen vom Kontext abhängen, brauchst du **einen Durchlauf, der den Kontext mitführt** — keine Kette. Und teste Idempotenz per Fuzz, nicht per Handfixture: meine Handfixture hatte zufällig ein `\n` am Ende und verfehlte den Fehler.

---

## 5 · Heuristiken, die raten, löschen Prosa

**Was passierte.** „Kurzer, unpunktierter Listeneintrag = Katalogeintrag" klang vernünftig. Es löschte echte Argumente in Notizform — und eine Slop-Listicle aus fünf kurzen Bullets wäre komplett verschwunden, also genau das, was der Detektor fangen soll.

**Regel.** In einem Werkzeug, das Text **entfernt**, bevor er bewertet wird, ist jede Rate-Heuristik gefährlich: ein falsches Behalten kostet einen Score-Punkt, ein falsches Entfernen versteckt die Passage. Verlange ein **explizites Merkmal** (Anführung, Betonung, Code-Span), keine Schätzung aus Länge oder Form.

---

## 6 · Die eigene Doku umformulieren, bis der Detektor schweigt

**Was passierte.** Beim Schreiben eines neuen Absatzes in `docs/USER-GUIDE.md` löste meine eigene Formulierung ein Muster aus. Ich habe umformuliert („table of contents" → „contents listing"). Der Absatz wurde grün, der Defekt blieb.

Das ist die Goodhart-Bewegung, vor der `docs/SCORE-GOVERNANCE.md` warnt: die Metrik wird zum Ziel, gemessen wird nichts mehr. Ich habe es in #88 offengelegt und `docs/DOC-STYLE.md` verbietet es jetzt ausdrücklich.

**Regel.** Wenn ein Signal in eigener Prosa feuert, gibt es zwei zulässige Antworten: die Prosa ist wirklich schlecht und wird besser, oder das Signal ist falsch und bekommt ein Ticket. Die Wortwahl zu drehen ist keine dritte.

---

## 7 · Leckage über die Initialisierung, nicht über die Daten

**Was passierte.** Für #85 baute ich eine Kreuzvalidierung: Gewichte je Fold nur auf dem Trainingsteil fitten, auf dem Rest messen. Ein Test prüfte, dass der Kalibrator **keinen** Held-out-Text zu sehen bekommt — und der Test war grün und korrekt.

Der Kalibrator startete die Coordinate Ascent trotzdem bei `DEFAULT_WEIGHTS`. Die sind auf dem **gesamten** Korpus gefittet, also auch auf jedem Held-out-Fold. Und weil Ascent ein Gewicht nur bei echter Verbesserung bewegt, blieb eine gut gesetzte Dimension einfach stehen: **vier von fünf Folds behielten die vollen Korpusgewichte unverändert** und bewerteten ihre Held-out-Texte mit Gewichten, die auf genau diesen Texten gefittet waren.

Das Symptom stand in meiner eigenen Ergebnistabelle: der Held-out-Recall war auf drei Stellen identisch zum In-sample-Recall, auf beiden Engines. Ich habe die Tabelle veröffentlicht, ohne mich das zu fragen.

**Regel.** Ein Leckage-Test, der prüft *welche Daten* ein Verfahren sieht, deckt nur einen Kanal ab. Frag zusätzlich: **womit fängt das Verfahren an, und was weiß dieser Startwert?** Initialisierung, Hyperparameter, Schwellen, Feature-Listen — alles, was aus den Daten stammt, ist ein Kanal. In diesem Repo gibt es davon mindestens drei (#85 Gewichte, #107 Signalinventare, und die Schwelle 0.40 selbst).

Und: wenn zwei Zahlen, die sich unterscheiden **sollten**, auf drei Stellen gleich sind, ist das ein Befund, kein Zufall.

---

## 8 · „Die Suche findet nichts" ist nicht „es gibt nichts zu finden"

**Was passierte.** Nach dem Fix aus Falle 7 startete jeder Fold bei uniformen Gewichten. Die Ascent fand daraufhin **in keinem einzigen Fold** einen verbessernden Zug. Ich schloss daraus: der Korpus kann zwischen Gewichtsvektoren nicht unterscheiden, die Kalibrierung ist fast nichts wert — und machte ein Ticket dafür auf (#106).

Das Review zeigte die Gegenprobe: `DEFAULT_WEIGHTS` schlägt den uniformen Vektor auf **vier von fünf Trainingsfolds**. Es gibt also bessere Punkte, die Ascent kommt nur nicht hin — das Ziel ist stückweise konstant, die Suche akzeptiert nur eine Verbesserung durch **eine** Koordinate, und der uniforme Vektor liegt auf einem Plateau, das mehrere gleichzeitig braucht.

Der Fehlschluss war also: aus dem Verhalten eines Optimierers auf die Struktur des Problems geschlossen. Das ist Goodhart in der Rückrichtung — statt die Metrik zum Ziel zu machen, habe ich das Versagen der Suche zur Eigenschaft der Welt erklärt.

**Regel.** Bevor du aus einem Nullergebnis etwas folgerst: **konstruiere einen Gegenbeleg und lass ihn scheitern.** Hier waren das drei Zeilen — zwei bekannte Vektoren auf denselben Trainingsfolds vergleichen. Wenn der Gegenbeleg gelingt, war dein Nullergebnis ein Werkzeugproblem.

---

## 9 · Ein Skript, das nie jemand ausgeführt hat

**Was passierte.** `eval/calibrate.py` hielt eine hartcodierte Kopie der Gewichtsnamen mit 13 Einträgen. Der Scorer hatte längst 14 (`portability`, #14). Jeder Aufruf starb mit `KeyError: 'portability'`.

Das Skript ist die **Herkunftsangabe der ausgelieferten Gewichte** — der Kommentar im Scorer verweist darauf. Es stand in der Doku, es stand in `docs/EVALS.md` als L3-Werkzeug, und es war nicht lauffähig. Kein Gate hat es gemerkt, weil kein Test es je aufgerufen hat.

Das war der **sechste** Fundort derselben Fehlerklasse in zwei Sessions: eine zweite Kopie von Daten, die hinter ihrer Quelle zurückgefallen ist. Die anderen fünf: `src/scorer.py`, `slop_scorer.py` (zweimal), `genre_profiles.py`, `slop_classifier.py`.

**Regel.** Jedes Skript, das die Doku als Beleg für eine Zahl anführt, braucht einen Test, der es **ausführt** — und sei es mit `rounds=0` auf zwölf Zeilen. Ein Werkzeug, das niemand aufruft, ist keine Herkunftsangabe, sondern eine Behauptung.

Und beim nächsten Konstantenpaar zuerst: **kann eine dieser beiden Listen die andere lesen, statt sie zu kopieren?** Sechs von sechs Fällen wären damit nicht entstanden.

---

## Querschnitt

Fünf der ersten sechs sind derselbe Fehler in verschiedenen Kostümen: **etwas sah geprüft aus, ohne geprüft zu sein.** Ein Test, der nicht fehlschlagen kann; eine Schwelle, die nicht verletzt werden kann; ein Vergleich gegen die falsche Zahl; eine Fixture, die den Fehlerfall verfehlt; ein Satz, der umgangen statt korrigiert wurde.

Die Gegenfrage, die in dieser Codebasis am meisten wert ist: **„Was müsste wahr sein, damit das hier rot wird — und kann ich das herstellen?"**

Die drei neuen sind eine Stufe härter, weil dort **kein Gate versagt hat**: die Tests waren grün und hatten recht, sie prüften nur die falsche Frage. Für Messungen lautet die Gegenfrage deshalb anders:

**„Welche Zahl müsste sich unterscheiden, wenn meine Erklärung stimmt — und tut sie das?"**

Bei Falle 7 hätte sie sofort gegriffen (Held-out- und In-sample-Recall waren identisch, obwohl sie es nicht sein durften). Bei Falle 8 auch (zwei bekannte Vektoren vergleichen, drei Zeilen). Beide Male habe ich die Zahl stattdessen veröffentlicht und ein Review hat sie zurückgeholt.

Daraus die einzige Prozessregel, die ich diesem Paket hinzufügen würde: **eine neu gemessene Zahl geht nicht in einen PR-Body, bevor du einen Weg gesucht hast, sie zu widerlegen.** Das kostet Minuten. Die Korrektur kostet einen Review-Zyklus und die Glaubwürdigkeit jeder Zahl daneben.
