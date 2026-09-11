# TOOL-EVALUATION.md — Wie man Anti-Slop-Tools evaluiert

**Status:** verbindliche Checkliste für die Bewertung fremder Slop-/KI-Text-Detektoren · **Issue:** GitHub #71 (GL-Sync #1113) · **Verwandt:** #38 (Positionierung), #41 (Labeled Corpus + FP-Gate), #48 (Meta-Self-Check), docs/EVALS.md (eigene Drei-Level-Architektur)

---

## Warum diese Checkliste existiert

Der Detektor-Markt ist Gresham-getrieben: Werkzeuge ohne nachprüfbare Evals verdrängen prüfbare Detektoren, weil „erkennt KI-Text“ billiger zu behaupten ist als zu belegen. Die Referenzdatenlage ist dünn, aber eindeutig: Weber-Wulff et al. (2023) maßen alle 14 untersuchten kommerziellen KI-Text-Detektoren unter 80 % Akkuratesse — bei mehreren lag die Trefferquote auf zufälligem Niveau. Wer ein fremdes Tool einsetzt oder empfiehlt, ohne diese Lücke zu prüfen, erbt dessen unbelegte Behauptungen.

Diese Checkliste ist ein einseitiger Kriterienkatalog: Sie definiert, welche Nachweise ein Detektor schuldig ist, bevor er als Bewertungsstandard für fremde Texte eingesetzt wird. Sie ist bewusst anspruchsloser als die eigene Architektur aus docs/EVALS.md — ein fremdes Tool muss nicht unser L1/L2/L3 erfüllen, aber es muss die Minimalnachweise dieser Liste offenlegen.

## Die Checkliste (L2-Abwehr)

Fünf Nachweise, geordnet nach Prüfbarkeit. Ein Tool, das keines davon liefert, ist kein bewerteter Detektor, sondern eine Behauptung mit Schnittstelle.

1. **Gelabelter Korpus publiziert?** — Gibt es einen öffentlich einsehbaren, gelabelten Testkorpus (Texte + Labels + ggf. Quellen), auf dem die beworbenen Zahlen messbar entstehen? Belegtquote, Hard Negatives und Genre-Streuung analog adr/0005 sind Bonus; Minimalanspruch ist: derselbe Korpus muss von Dritten gerunner werden können. Ohne das ist jede Prozentzahl In-Sample-Marketing.

2. **FP/FN unabhängig gemessen?** — Werden False-Positive- und False-Negative-Raten von einer Partei berichtet, die nicht das Tool verkauft? Selbstberichtete Zahlen auf selbst gewählten Texten sind keine Messung. Wurde der Korpus gefittet (Gewichte, Schwellen), muss die Kommunikation das sagen — vgl. docs/EVALS.md zum In-Sample-Problem.

3. **Zählregeln dokumentiert?** — Was zählt als ein Treffer: pro Signal, pro Satz, pro Dokument? Doppelt gezogene Overlaps, Multiplikatoren, Aggregation (Summe vs. gewichtetes Mittel) müssen schriftlich sein. Ohne Zählregeln sind zwei Detektoren nicht vergleichbar und ein Score nicht reproduzierbar.

4. **Quote-/Markup-Handling definiert?** — Werden zitierte Passagen, Code-Fences, Tabellen und Auszeichnungen vom Scoring ausgenommen (Präpass) oder mitgezählt? Ein Detektor, der zitierten Text als Beleg für Autoren-Slop wertet, bestraft korrektes Zitieren — vgl. #23/#69 und `scripts/self_check_docs.py`.

5. **Control-Set-Verhalten öffentlich?** — Wie verhält sich das Tool auf einem bekannten Satz handgeschriebener Kontrolltexte, inklusive Hard Negatives? Werden bekannte Fehlschläge als Register geführt (Known-FN) oder verschwiegen? Ein Tool ohne dokumentierte Schwächen hat keine dokumentierten Schwächen — das ist ein rotes Tuch, kein Feature.

## Bewertungsstufen

- **Bewertbar:** alle fünf Nachweise offen. Dann ist das Tool vergleichbar; Zahlen mit Vorsicht übernehmen, Zählregeln beachten.
- **Teilweise bewertbar:** Nachweise 1 und 3 vorhanden, Rest nicht. Für Orientation brauchbar, nie als Gate.
- **Behauptung:** keine Publikation von Korpus oder Messung. Nicht einsetzen, nicht zitieren, nicht empfehlen — auch nicht als „bessere Intuition“.

## Anwendung im eigenen Kontext

Die Checkliste ist der Bewertungsstandard für Fremd-Tools im Sinne von #38: Sie grenzt die eigene Positionierung („Detector, kein Rewriter“) ab, indem sie misst, ob fremde Detektoren überhaupt messen. Sie ersetzt nicht die eigene Eval-Architektur (docs/EVALS.md, #41 Corpus + FP-Gate, #48 Meta-Self-Check) — sie ist der Spiegel: Ein Tool, das diese Liste nicht besteht, hätte unsere Gates nicht einmal erreicht.

## Referenz

- Weber-Wulff, M., et al. (2023): *Testing of detection tools for AI-generated text.* International Journal for Educational Integrity 19, 26. — 14 kommerzielle Detektoren, alle < 80 % Akkuratesse.
- `research/meta-slop-2026-08-24/report.md` Abschnitt b/f (Meta-Slop-Research, Ursprung dieses Katalogs).
