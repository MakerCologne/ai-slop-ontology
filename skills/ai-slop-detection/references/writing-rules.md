# Writing Rules — Praevention beim Schreiben (write-side)

> Gegenpart zur Detektion: Diese Regeln wirken vor und waehrend des Schreibens,
> nicht nachtraeglich. Quelle: Arjan Leuschner, 16.09.2026 (Issue #228, P1 aus dem
> Detection-vs-Prevention-Audit). Schwestersdokument: `authoring-rules.md` (Aufzaehlungen/Rhythmik).

## Grundsatz

Struktur entsteht aus Inhalt, Situation und Kommunikationsabsicht - nicht aus
wiederkehrenden LLM- oder Marketingmustern. Ziel ist kein simuliertes Menschsein,
sondern inhaltliche Praezision und natuerliche strukturelle Varianz.

## 1. Kernregel fuer Satzanfaenge: Inhalt statt Ankuendigung

Beginne moeglichst mit dem Inhalt, nicht mit der Ankuendigung des Inhalts.

Schwaecher: "Ich denke, dass hier vor allem das Prozesswissen entscheidend ist."
Direkter: "Entscheidend ist hier vor allem das Prozesswissen."

Schwaecher: "Spannender Punkt. Eine weitere Frage waere, wie Unternehmen dieses Wissen langfristig erhalten."
Direkter: "Wie Unternehmen dieses Wissen langfristig erhalten, bleibt dabei noch offen."

Schwaecher: "Ich moechte mich noch einmal fuer das angenehme Gespraech bedanken."
Direkter: "Vielen Dank noch einmal fuer das angenehme Gespraech."

Je nach Kontext kann ein voellig anderer Einstieg besser sein:
"Unser Gespraech vom Dienstag hat bei mir noch etwas ausgeloest ..."

**Wann nicht:** Die Ankuendigung kann selbst der Inhalt sein - z. B. in
Verhandlungen ("Ich moechte hier ausdruecklich widersprechen") oder wenn die
eigene Positionierung die Aussage ist. Die Regel erzeugt KEINE mechanische
Transformation von "Ich" zu Passivkonstruktionen.

## 2. Einstiegstypen (Wahl aus dem Kontext - keine Ersatztabelle)

Waehle zwischen Einstiegstypen, statt verbotene Formulierungen durch neue
Standardformulierungen zu ersetzen. Fuenz verbotene Anfaenge plus fuenf neue
Standardanfaenge erzeugen nur den naechsten Slop.

| Typ | Beispiel |
|---|---|
| Sachverhalt | "Viele dieser Informationen existieren bereits." |
| Beobachtung | "In der Praxis zeigt sich dabei haeufig ein anderes Problem." |
| Konsequenz | "Damit verschiebt sich die eigentliche Aufgabe." |
| Konkreter Bezug | "Bei Produktionsprozessen sieht das anders aus." |
| Anlass | "Unser Gespraech vom Dienstag ist mir noch einmal durch den Kopf gegangen." |
| Empfaengerbezug | "Ihre Beschreibung des Vorgehens passt gut zu ..." |
| Handlung | "Fuer den naechsten Schritt wuerde ich ..." |
| Kontrast | "Bei bestehenden Produktionsanlagen greift diese Logik allerdings zu kurz." |
| Frage | "Wie viel davon ist heute tatsaechlich dokumentiert?" |

Die Wahl muss aus dem Kontext erfolgen - nicht rotierend, nicht zufaellig.

## 3. "Ich" differenziert

Kein pauschales Verbot von "Ich". Pruefe stattdessen:

1. Ist die Person selbst tatsaechlich Gegenstand der Aussage?
2. Ist die persoenliche Haltung relevant?
3. Wird mit "Ich" lediglich ein hoeflicher oder vorsichtiger Anlauf erzeugt?
4. Laesst sich direkt mit Anlass, Empfaenger, Beobachtung, Sachverhalt oder Handlung beginnen?

Am Anfang von E-Mails: Ist der erste Satz unnoetig senderzentriert?

Schwaecher: "Ich wuerde gerne einen Termin mit Ihnen vereinbaren."
Besser: "Kurzfristig wuerde ich gerne einen Termin mit Ihnen vereinbaren."
Kontextabhaengig direkter: "Fuer die weitere Abstimmung wuerde ein kurzer Termin in der kommenden Woche gut passen."

## 4. LinkedIn-Kommentare

Typischer KI-Ablauf: Lob -> Paraphrase des Posts -> vorsichtige Ergaenzung -> offene Frage.
Dieses Muster darf nicht zum Default werden. Ein Kommentar darf unmittelbar mit
dem zusaetzlichen Gedanken beginnen.

Schwaecher: "Spannender Punkt. Ich denke, ein weiterer wichtiger Aspekt ist die Frage, wie viel Prozesswissen tatsaechlich verfuegbar ist."
Besser: "Dazu kommt fuer mich die Frage, wie viel Prozesswissen tatsaechlich verfuegbar ist."
Noch direkter: "Wie viel des relevanten Prozesswissens ist tatsaechlich verfuegbar, wenn erfahrene Mitarbeitende gerade nicht erreichbar sind?"

Fragen nur einsetzen, wenn wirklich eine Frage gestellt werden soll. Keine
rhetorische Frage lediglich als Engagement-Hook.

## 5. Absatzanfaenge

Dasselbe Prinzip oberhalb der Satzebene: Konnektoren ("Darueber hinaus", "Zudem",
"Ein weiterer wichtiger Punkt", "Gleichzeitig", "Abschliessend", "Zusammenfassend")
sind sinnvoll, duerfen aber nicht jeden Absatz kuenstlich verzahnen. Ein neuer
Absatz darf direkt mit seinem Inhalt beginnen.

## 6. Anzahl folgt dem Inhalt

Siehe `authoring-rules.md`: Die Anzahl genannter Elemente folgt dem Inhalt, nicht
einem Rhythmus. Ein Punkt, wenn einer relevant ist. Zwei, wenn zwei sinnvoll sind.
Vier, wenn vier noetig sind. Drei ist erlaubt - nur kein Default.

## 7. Varianz ohne Quoten

Keine Zufallsmaschine, keine festen Quoten ("20 % Fragen, 30 % kurze Einstiege").
Regel: Vermeide unnoetige Wiederholung desselben rhetorischen Musters innerhalb
eines Textes und ueber mehrere generierte Varianten hinweg. Varianz ist Mittel zum
Zweck - sie darf Praezision, Ton und Verstaendlichkeit nicht verschlechtern.

## Style-Prompt-Snippet (kondensiert, fuer die Erstgenerierung)

```
Beginne mit Inhalt statt mit der Ankuendigung des Inhalts. Waehle den Einstieg
aus dem Kontext (Sachverhalt, Beobachtung, Konsequenz, Bezug, Anlass,
Empfaengerbezug, Handlung, Kontrast oder eine echte Frage) - nicht aus
Standardformulierungen. "Ich" nur, wenn Person oder Haltung relevant sind.
Keine Lob-Paraphrase-Ergaenzung-Frage-Sequenz als Kommentar-Default. Keine
Dreiergruppen als Rhythmus; die Anzahl der Elemente folgt dem Inhalt.
Konnektoren duerfen nicht jeden Absatz eroeffnen. Keine rhetorischen Fragen ohne
Frageabsicht. Wiederhole dasselbe rhetorische Muster nicht ueber Varianten -
tausche nicht nur Woerter. Varianz nie auf Kosten von Praezision.
```

## Bezug zur Detektion

Wer trotzdem stolpert, faellt auf: `opener_announcement` (geplant, #230),
`engagement_comment_default` (geplant, #231), `ForcedTriad`, `RoboticRhythm`,
`LowOpenerDiversity`, `UniformLengthRun`. Die `keep_when`-Vorbehalte der Signale
sind die Grenze dieser Regeln: legitime persoenliche Haltung, bewusste Ankuendigung
und drei wirklich verschiedene Punkte sind kein Slop.
