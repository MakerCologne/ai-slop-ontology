# PITFALLS.md — sechs Fallen aus der Vorgängersession

Jede hier ist mir tatsächlich passiert, nicht ausgedacht. Vier davon hat erst ein Review gefunden, nachdem ich „alle Gates grün" gemeldet hatte.

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

## Querschnitt

Fünf der sechs sind derselbe Fehler in verschiedenen Kostümen: **etwas sah geprüft aus, ohne geprüft zu sein.** Ein Test, der nicht fehlschlagen kann; eine Schwelle, die nicht verletzt werden kann; ein Vergleich gegen die falsche Zahl; eine Fixture, die den Fehlerfall verfehlt; ein Satz, der umgangen statt korrigiert wurde.

Die Gegenfrage, die in dieser Codebasis am meisten wert ist: **„Was müsste wahr sein, damit das hier rot wird — und kann ich das herstellen?"**
