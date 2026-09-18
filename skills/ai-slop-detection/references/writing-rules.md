<<<<<<< HEAD
# Writing Rules — Einstiege, Ich-Bezug, Konnektoren (Praevention write-side)

> Gegenpart zum Detektor, Fortsetzung von `authoring-rules.md` (Dreierstrukturen,
> Rhythmik, Trenner, Asymmetrie). Dieses Dokument deckt Satzanfangs- und
> Einstiegsmuster ab. Quelle: Detection-vs-Prevention-Audit 15.09.2026
> (research/slop-prevention-audit/report.md, Arjan-Auftrag).

## Grundsatz / Kernregel

**Beginne mit Inhalt statt mit der Ankündigung des Inhalts.**

Typisches Slop-Muster: Der Satz startet mit einer Rahmung des Sprechers
("Ich denke, dass hier...", "Es ist wichtig zu beachten, dass...") und liefert
die eigentliche Aussage erst im Nebensatz nach. Direkteinstieg heisst: die
tragende Aussage steht im Hauptsatz, die Rahmung faellt weg oder rückt ans Ende.

- "Ich denke, dass hier die Fehlerbehandlung fehlt." -> "Entscheidend ist hier
  die fehlende Fehlerbehandlung." (oder schlicht: "Hier fehlt die
  Fehlerbehandlung.")
- "Zusammenfassend kann man sagen, dass die Migration riskant ist." -> "Die
  Migration ist riskant, weil ... (Begründung)."

## 1. Einstiegstypen-Katalog — Wahl aus dem Kontext, keine Ersatzliste

Einstiege werden nicht durch Ersetzen einer Formel durch eine andere Formel
besser (das erzeugt nur eine neue Slop-Signatur). Waehle den Einstiegstyp aus,
den Inhalt und Situation verlangen. Der Katalog dient der Auswahl, nicht als
Substitutionstabelle (ausdruecklich KEINE Verbot->Ersatz-Zuordnung).

| Typ | Funktion | Beispiel |
|-----|----------|----------|
| Sachverhalt | Zustand als erste Information | "Die Pipeline bricht seit Commit 4f2a bei den Integrationstests ab." |
| Beobachtung | Wahrgenommenes ohne Bewertung voranstellen | "Im Review faellt auf, dass drei Module dieselbe Utility duplizieren." |
| Konsequenz | Wirkung zuerst, Ursache danach | "Ohne Fix verliert der Cache bei jedem Restart alle Eintraege." |
| Konkreter Bezug | Direkt am konkreten Punkt/Objekt ansetzen | "Dein Punkt zur Retry-Logik trifft den Kern des Problems." |
| Anlass | Ereignis als Einstieg nennen | "Das Ausfallticket von gestern Abend hat zwei Lücken im Alerting aufgezeigt." |
| Empfängerbezug | Beim Adressaten beginnen | "Du hattest nach dem Stand der Migration gefragt." |
| Handlung | Tat-/Entscheidungssatz als Auftakt | "Wir haben den Rollback um 14:30 ausgefuehrt und das Monitoring angepasst." |
| Kontrast | Spannung/Gegensatz setzen | "Der Benchmark sah gut aus; im Staging bricht dieselbe Konfiguration ab." |
| Frage | Interesse bündeln (sparsam) | "Was passiert eigentlich mit den offenen Sessions beim Deploy?" |

**Wann nicht:** Kein Typ ist verpflichtend oder "besser". Ein Frage-Einstieg als
Dauerformel ist selbst ein Muster; ein Kontrast-Einstieg ohne tatsächlichen
Gegensatz ist konstruiert. Der Katalog ersetzt nicht die Pruefung, ob der erste
Satz ueberhaupt Information traegt.

## 2. "Ich" differenziert

1. "Ich" ist erlaubt und richtig, wenn die Person Gegenstand der Aussage ist
   ("Ich habe das Deployment um 14:30 ausgeloest.") oder wenn die Haltung als
   Haltung relevant ist ("Ich halte das Risiko fuer vertretbar, weil ...").
2. Sonst Direkteinstieg: "Ich glaube, dass die Doku unvollstaendig ist." ->
   "Die Doku ist unvollstaendig (Abschnitt 3 endet mitten im Satz)."
3. Erste Saetze von E-Mails auf Senderzentrierung pruefen: Beginnt der Text mit
   dem Sender ("Ich wollte kurz nachfragen, ...") oder mit dem Anlass/Empfaenger?
   Senderzentrierung am Anfang ist der klassische Slop-Opener.
4. **Keine mechanische Ich->Passiv-Transformation.** "Es wird davon ausgegangen,
   dass ..." ist nicht besser als "Ich gehe davon aus, dass ..." — es ist
   schlechter: unpersoenlicher, laenger, Verantwortung verschleiert. Wenn die
   Person relevant ist, bleib bei "ich".

**Wann nicht:** Persoenliche Verantwortung, Erfahrungsberichte, Meinungen mit
Begruendung brauchen das Ich. Ein Text ohne jedes Ich ist kein Zielzustand.

## 3. LinkedIn-Kommentare

1. Inhaltlicher Bezug statt Lob-Auftakt: Nicht "Toller Post!" als Fuell-Einstieg,
   sondern am konkreten Inhalt ansetzen ("Dein Punkt zur Latenz bei
   Edge-Deployments gilt doppelt fuer ...").
2. Die Sequenz Lob -> Paraphrase -> Ergaenzung -> Frage ist ein erkanntes
   Kommentar-Slop-Muster (LSkommentator, LinkedIn-Kommentar-Slop). Sie ist nicht
   verboten, aber nicht als Default-Sequenz für jeden Kommentar; wenn sie
   eingesetzt wird, muss jedes Element tragen (echtes Lob, eigene Ergaenzung,
   echte Frage).
3. Ein Kommentar, der nur bestaetigt ("Sehr wahr!"), ist kein Kommentar — dann
   lieber Reaktion statt Antwort.

**Wann nicht:** Echtes, spezifisches Lob am Anfang ist legitim ("Deine Analyse
der Retry-Kosten war der beste Teil des Threads — sie hat mich veranlasst, ...").
Der Unterschied liegt in Spezifität und Folgesatz, nicht im Verbot.

## 4. Anzahl folgt dem Inhalt

"Die Anzahl folgt dem Inhalt — 3 ist erlaubt, nur kein Default." Details und
Beispiele: `authoring-rules.md` Abschnitt 1 (Dreierstruktur, kuenstliche
Rhythmik). Gilt entsprechend fuer Aufzaehlungen, Beispiele, Argumente.

**Wann nicht:** Wenn es exakt drei tragende Punkte gibt, sind drei Punkte
korrekt — erzwungen keine zwei oder vier.

## 5. Varianz als Mittel zum Zweck

Abwechslungsreiche Einstiege und Satzformen erhoehen Glaubwuerdigkeit und
Lesbarkeit — aber Varianz ist Mittel zum Zweck, kein Selbstzweck. **Explizit
keine Quoten** ("jeder dritte Satz ein kurzer", "20 % Fragen"): Quoten erzeugen
eine neue, messbare Regelmaessigkeit und verschlechtern Praezision.

**Wann nicht:** Wenn Praezision, Vollstaendigkeit oder Verstaendlichkeit unter
erzwungener Abwechslung leiden, hat der Inhalt Vorrang.

## 6. Konnektor-Absaetze

"Darüber hinaus", "Zudem", "Abschließend" u.a. strukturieren Argumente — sie
sind sinnvoll, wenn sie eine echte Beziehung (Ergaenzung, Steigerung, Abschluss)
ausdruecken. Nicht jeder Absatz braucht einen Konnektor-Auftakt; wenn jeder
Absatz mit "Darüber hinaus"/"Zudem" beginnt, wird die Struktur formelhaft und
der Text liest sich wie eine Aufzaehlung in Prosa.

**Wann nicht:** In juristischen und formalen Textsorten (Genre-Profile nach
ADR-0004) sind praepositionierte Konnektoren etabliertes Genre-Merkmal und
durchaus angemessen; auch in langen argumentativen Texten markieren sie echte
Gelenkstellen. Siehe Genre-Opt-in, `adr/0004-genre-opt-in.md`.

## Hard Negatives (keep_when-Disziplin)

Diese Faelle sind KEIN Slop und duerfen von praeventiven Regeln nicht
wegoptimiert werden:

1. **Legitimes "Ich denke, dass X"** — wenn die Haltung als Haltung relevant
   ist und begruendet wird ("Ich denke, dass wir den Rollback fahren sollten,
   weil der Datenverlust im Worst Case unkompensierbar ist."). Das Ich traegt
   hier Verantwortung und Unterscheidung (Schaetzung vs. Fakt); ein
   Passiv-Ersatz wuerde die Aussage schlechter machen. Praeventionsregel:
   pruefe, ob Person/Haltung relevant ist — nicht: streiche "ich denke".
2. **"Darüber hinaus" im juristischen Genre-Profil** — Zivilprozessuale und
   gesetzestechnische Texte nutzen additive Konnektoren als etablierte
   Strukturform; Praevention greift hier nicht (ADR-0004 Genre-Opt-in).

## Style-Prompt-Snippet (Erstgenerierung)

Kondensiert fuer den Schreibauftrag / System-Prompt, wenn Text von vornherein
slop-arm entstehen soll:

```
Beginne Saetze mit Inhalt, nicht mit der Ankuedigung des Inhalts ("Ich denke,
dass ..." -> Aussage direkt). Waehle Einstiege aus dem Kontext: Sachverhalt,
Beobachtung, Konsequenz, konkreter Bezug, Anlass, Empfängerbezug, Handlung,
Kontrast, Frage — keine Standardformeln, keine Ersetzungstabelle. "Ich" nur,
wenn Person oder Haltung relevant sind; nie mechanisch ins Passiv. Kein
Dreier-Default: Anzahl folgt dem Inhalt. Varianz ja, aber keine Quoten.
Konnektor-Absaetze nur bei echter Gliederung. Kein Lob-Auftakt ohne
inhaltlichen Bezug; Lob->Paraphrase->Ergaenzung->Frage nie als Default-Sequenz.
```

## Bezug zu Detektor-Signalen (beiaktiv)

Wer trotzdem stolpert, faellt auf: `LowOpenerDiversity` (Satzanfangs-Wiederholung),
`AI-Phrase-Kategorien` (opening/closing formulas), LinkedIn-Kommentar-Slop
(Lob-Paraphrase-Sequenz). Die `keep_when`-Vorbehalte der Signale sind die
Grenze: Die Hard Negatives oben sind die dokumentierte Gegenseite. Praevention
ist write-side und hat **keinen Score-Einfluss** (ADR-0006: detect-only-Module;
dieses Dokument ist reine Referenz).
=======
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
>>>>>>> origin/master
