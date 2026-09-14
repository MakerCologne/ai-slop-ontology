# EVALUATING-DETECTORS.md — Wie man Detektoren für KI-Slop evaluiert

**Status:** Kriterienkatalog (slopgh#71, „L2-Abwehr-Checkliste") · **Art:** einseitiger Bewertungsstandard für Fremd-Tools · **Bezug:** #38 (Positionierung), #41/#48 (eigenes Eval-Fundament), Weber-Wulff et al. 2023 (alle 14 getesteten kommerziellen GPT-Detektoren unter 80 % Akkuratesse)

---

## Warum dieses Dokument existiert

Der Markt für KI-Text-Detektoren ist Gresham-getrieben: Klone ohne messbare Evals verdrängen prüfbare Detektoren, weil „erkennt KI-Text" auf einer Landing Page billiger zu haben ist als ein gelabelter Korpus. Wer ein Fremd-Tool bewerten will — kaufen, einsetzen, empfehlen —, braucht Kriterien, die nicht vom Hersteller selbst definiert werden. Diese Checkliste ist die Antwort: Sie zählt auf, welche Nachweise ein Detektor schuldig ist, bevor seine Zahl etwas bedeutet.

Die Checkliste ist auch nach innen gerichtet. Jeder Punkt ist eine Frage, die ein Detektor mit dem Etikett „evaluiert" aus diesem Repo beantworten können muss — die Antworten stehen in `docs/EVALS.md`.

## Die Checkliste

Ein Detektor gilt erst dann als evaluierbar, wenn alle mit **Muss** markierten Punkte beantwortet sind. Punkte mit **Soll** sind starke Hinweise, kein Ausschlusskriterium.

### 1. Gelabelter Korpus

- **Muss:** Es existiert ein gelabelter Korpus, und er ist publiziert oder zumindest in Umfang und Zusammensetzung beschrieben (n_positiv, n_negativ, Genres, Sprachen, Quellen). Eine Zahl ohne Korpus ist Marketing.
- **Muss:** Die Labels sind unabhängig vom Detektor entstanden — handgelabelt oder aus natürlichen Klassen (bekannt menschlich / bekannt maschinell), nicht „so, wie das Tool es klassifiziert hat". Zirkuläre Labels erzeugen zirkuläre Akkuratesse.
- **Soll:** Der Korpus enthält Hard Negatives — handgeschriebene Texte, die Slop-Mustern ähneln. Ein Detektor, der nur offensichtliche Fälle trennt, misst nur die leichte Hälfte des Problems.

### 2. Messung von FP und FN — getrennt

- **Muss:** False-Positive- und False-Negative-Rate werden separat berichtet, nicht nur eine aggregierte Akkuratesse oder F1. Bei seltener Positivklasse kann eine hohe Akkuratesse bedeuten, dass das Tool einfach alles negativ nennt.
- **Muss:** Die Raten beziehen sich auf einen Schwellwert, und der Schwellwert ist genannt. „98 %" ohne Threshold ist nicht reproduzierbar.
- **Soll:** Die Messung ist Held-out oder kreuzvalidiert. In-Sample-Zahlen (gefittet und gemessen auf demselben Korpus) sind Obergrenzen, keine Generalisierungsschätzung — siehe `docs/EVALS.md`, Abschnitt „Welche Zahl ist welcher Art".
- **Soll:** Es gibt eine Angabe zur Streuung — Fold-Varianz, Konfidenzintervall oder mindestens Wiederholungen mit unterschiedlichen Seeds.

### 3. Zählregeln und Vorverarbeitung dokumentiert

- **Muss:** Wie werden Texte normalisiert? Zählen Emojis, Code, Zitate, Listen, Tabellen zur Stimme oder werden sie vom Präpass entfernt? Ein Detektor, der seine Vorverarbeitung nicht nennt, misst ein unbekanntes Artefakt.
- **Muss:** Ist das Ergebnis deterministisch bei gleicher Eingabe (Regelwerk), oder ist es stochastisch (LLM-Judge)? Stochastische Detektoren müssen Seed-Politik und Temperatur nennen, sonst ist keine Wiederholung möglich.
- **Soll:** Die Signal- beziehungsweise Kategorienliste ist offen gelegt oder zumindest in Klassen beschrieben. Blackbox-Kategorien machen Fehleranalysen unmöglich.

### 4. Control-Set-Verhalten

- **Muss:** Wie verhält sich das Tool auf einem kleinen, fixen Kontrollset, das über Zeit gleich bleibt? Ein Detektor, der auf dasselbe Set bei jedem Aufruf verschiedene Antworten liefert, kann nicht als Gate dienen.
- **Soll:** Bekannte Fehlschläge sind dokumentiert (known-FN-Register), statt stillschweigend zu verschwinden. Register mit Auflösungsdatum sind ein Reifesignal, kein Schwächezeichen.

### 5. Operationale Grenzen

- **Muss:** Sprachabdeckung ist genannt. Ein Detektor, der nur auf Englisch kalibriert ist, und dann auf Deutsche Texte losgelassen wird, produziert Zahlen unbekannter Güte.
- **Soll:** Angabe, welche Textlängen und Genres bewertet wurden — ein Tool, das nur auf 500-Wörter-Essays gemessen wurde, ist für Tweet-Single-Frames nicht validiert.
- **Soll:** Aussage zur Anfälligkeit für gezieltes Rewriting (Evasion). Detektoren, die das nicht messen, überleben den Kontakt mit motivated adversaries nicht.

### 6. Unabhängigkeit

- **Muss:** Wer hat die Messung gemacht? Hersteller-Selbstauskünfte zählen nur, wenn die Messmethode (Korpus, Skripte) nachprüfbar offengelegt ist.
- **Soll:** Es existiert mindestens eine externe Messung, die nicht vom Hersteller beauftragt oder kontrolliert wurde.

## Scorecard

Ein Tool wird gegen alle Muss-Punkte geprüft; jedes unbeantwortete Muss ist ein roter Punkt, nicht eine Lücke zum Wohlwollen. Das Ergebnis ist eine Tabelle: Punkt, erfüllt/nein/nicht beantwortet, Beleg-Link. Ohne Beleg-Link gilt „nicht beantwortet".

## Abgrenzung

Diese Checkliste bewertet Detektoren von außen. Wie dieses Repo seine eigenen Detektoren evaluiert, steht in `docs/EVALS.md` (L1/L2/L3-Architektur), `docs/SCORE-GOVERNANCE.md` (Gewichte, Gates) und `docs/METHODOLOGY.md` (Methodenregister). Die Checkliste hier ist der Teil davon, der sich gegen Gresham richtet: Sie macht die Frage „wo ist dein Korpus?" billig genug, um sie immer zu stellen.

---

*Quelle: research/meta-slop-2026-08-24/report.md (Abschnitt b/f) · Umsetzung: slopgh#71 (btm-openclaw-platform #1113)*
