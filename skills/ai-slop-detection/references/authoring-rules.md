# Authoring Rules — Praevention statt Nachbesserung

> Gegenpart zum Detektor: Diese Regeln schreiben Slop-Muster gar nicht erst.
> Quelle: Arjan Leuschner, 15.09.2026 (Dreierstrukturen/Rhythmik); Erweiterung
> um Satzanfangs-/Einstiegstypen-Regeln in Vorbereitung (Detection-vs-Prevention-Audit).

## Grundsatz

Schreibe nicht mit dem Ziel, KI-Slop nachtraeglich erkennen zu lassen. Formuliere
von Anfang an so, dass typische Slop-Muster seltener entstehen. Struktur entsteht
aus Inhalt, Situation und Kommunikationsabsicht - nicht aus wiederkehrenden
LLM- oder Marketingmustern.

## 1. Aufzaehlungen und kuenstliche Rhythmik

1. Vermeide die automatische Dreierstruktur. Sprachmodelle und Marketingtexte
   ordnen Begriffe, Beispiele und Aussagen gern in drei Elemente, auch wenn der
   Inhalt diese Anzahl nicht verlangt ("Menschen. Prozesse. Technologie.",
   "Einfach. Schnell. Sicher.", "Strategie | Umsetzung | Wirkung",
   "verstehen, gestalten, transformieren").
2. Solche Dreierfiguren sind rhetorisch legitim, wirken durch haeufige Verwendung
   aber schnell formelhaft.
3. Die Anzahl der genannten Elemente folgt dem Inhalt, nicht einem gewuenschten
   Rhythmus: manchmal ein zentraler Begriff, manchmal zwei Aspekte, bei Bedarf
   vier oder mehr konkrete Punkte. Drei nur dann, wenn tatsaechlich genau drei
   sinnvoll sind.
4. Vermeide kuenstlich markante Aneinanderreihungen mit Punkten, Pipes, Hashtags
   oder aehnlichen Trennern, wenn sie primuer nach Slogan, Agenturtext oder
   LinkedIn-Marketing klingen.

## 2. Asymmetrie ist erlaubt

1. Texte duerfen asymmetrisch sein: unterschiedlich lange Aufzaehlungen,
   wechselnde Satzformen, gelegentlich unvollstaendige rhetorische Muster wirken
   haeufig natuerlicher als konsequent ausbalancierte Formulierungen.
2. Optimiere nicht rhetorische Perfektion, sondern inhaltliche Praezision und
   natuerliche sprachliche Varianz.
3. Erzwingen Sie keine Varianz-Quoten (keine "20 % Fragen, 30 % kurze Einstiege").
   Varianz ist Mittel zum Zweck und darf Praezision und Verstaendlichkeit nicht
   verschlechtern.

## 3. Bezug zu Detektor-Signalen (beiaktiv)

Wer trotzdem stolpert, faellt auf: `ForcedTriad` (inkl. Nomen-/Verb-Triaden und
Staccato-Dreier), `DecorativeSeparatorTriad` (Pipes/Hashtags), `RoboticRhythm`,
`UniformLengthRun`, `LowOpenerDiversity`. Die `keep_when`-Vorbehalte der Signale
sind die Grenze: drei wirklich verschiedene, einzeln tragende Punkte sind kein Slo.
