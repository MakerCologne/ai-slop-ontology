# TOOL-EVAL-CHECKLIST.md — Wie man Anti-Slop-Tools evaluiert

**Status:** verbindlicher Kriterienkatalog für Fremd-Tools (v1.0.0, Issue #71) · **Anlass:** Der Markt ist Gresham-getrieben — Klone ohne nachweisbare Evals verdrängen prüfbare Detektoren. Weber-Wulff et al. (2023) testeten 14 kommerzielle KI-Textdetektoren; keiner erreichte 80 % Akkuratesse, und die Ergebnisse waren auf denselben Texten zwischen Läufen instabil. Wer ein Tool bewertet oder adopts, braucht eine Mindestliste an Prüffragen, die ein Anbieter nicht mit Marketing beantworten kann.
**Verwandt:** docs/EVALS.md (L1/L2/L3 — wie wir *uns selbst* messen), Issue #38 (Positionierung "Detector, kein Rewriter"), #41 (Benchmark-Korpus), #48 (Meta-Self-Check), docs/SCORE-GOVERNANCE.md, adr/0005 (Benchmark-Disziplin).

---

## Der Kern

Ein Detektor ist nur so gut wie die **unabhängigste Zahl**, die er publiziert. Alles andere — Demos, Screenshots, "99 % accuracy" ohne Kontext — ist Marketing. Diese Checkliste prüft, ob die Zahlen existieren und ob sie etwas beweisen.

## Die zehn Fragen

1. **"Ist ein gelabelter Testkorpus publiziert?"** — Ohne öffentlichen Korpus (Größe, Label-Herkunft, Genre-Mix) ist jede Zahl reproduzierbar. Kategorie ist Minimum, Prozent-Angabe ohne Korpusangabe ist ein No-Go.
2. **"Sind FP und FN unabhängig gemessen?"** — In-Sample-Zahlen (auf dem Korpus gefittet, auf demselben Korpus gemessen) sind keine Generalisierungsschätzung. Gefordert: Kreuzvalidierung oder ein echter Held-out-Split (vgl. docs/EVALS.md §"Welche Zahl ist welcher Art").
3. **"Sind die Zählregeln dokumentiert?"** — Was zählt als ein Signal? Ein Dokument mit fünf Vorkommen derselben Phrase: 5 Treffer oder 1? Ohne Zählregel sind Precision/Recall nicht vergleichbar (vgl. `scripts/count_signals.py`).
4. **"Wie wird Quote- und Markup-Handling gemacht?"** — Ein Detektor, der zitierte Beispiele, Code-Fences und Tabellen als eigene Stimme des Autors scored, produziert FPs by construction. Gefordert: dokumentierter Präpass oder äquivalentes Ausschlussverfahren.
5. **"Gibt es ein öffentliches Control-Set-Verhalten?"** — Hard Negatives (handgeschriebene, saubere Texte, die Signale zufällig streifen) sind der härteste FP-Test. Wie verhält sich das Tool darauf? "Keine Hard Negatives im Test" = Testaussage unbrauchbar für FP-Raten.
6. **"Ist der Threshold begründet?"** — Eine Schwelle ohne Begründung (warum 0.40 und nicht 0.50?) ist ein Stellschrauben-Knopf, kein Qualitätsmerkmal. Begründungen aus Korpus-Statistik gelten, aus "gefühlt passend" nicht.
7. **"Ist das Tool deterministisch?"** — LLM-Judges ohne Temperatur-Disziplin und Seed liefern zwischen Läufen andere Scores. Gefordert: reproduzierbare Läufe (Fixtures + Schwellen, vgl. EVALS.md L1) oder dokumentierte Varianz.
8. **"Wird In-Sample ehrlich als In-Sample kommuniziert?"** — CHANGELOG, README, Demo-Seiten: Jede Zahl ohne Zusatz gilt als In-Sample (EVALS.md #85-Regel). Ein Tool, das Held-out-Zahlen nennt, ohne den Fit zu erwähnen, ist raus.
9. **"Existiert ein Ausnahmen-Register für bekannte FN?"** — Werkzeuge, die ihre eigenen Blindstellen dokumentieren (known-FN-Register, adr/0003), können falsch-negative Stellen beheben; Tools ohne Register wiederholen sie stillschweigend.
10. **"Wie wird mit Klassenumfang umgegangen?"** — F1 auf einem 50/50-Korpus sagt wenig über den Einsatz auf 95 % Clean-Text aus. Gefordert: Konfusionsmatrix und Basisraten-Angabe, nicht nur eine Aggregate-Metrik.

## Bewertungsschema

Vier Antworten "ja mit Beleg" auf die Fragen 1, 2, 4 und 5 sind die Eintrittskarte — ohne sie ist das Tool nicht evaluiert, sondern beworben. Fragen 3, 6–10 unterscheiden brauchbare von guten Detektoren. Ein "nein" auf Frage 8 ist ein Ausschlusskriterium: Wer In-Sample als Generalisierung verkauft, verkauft auch sonst Zahlen.

## Warum diese Liste existiert

Diese Checkliste ist zugleich Selbstverpflichtung: Sie ist so formuliert, dass dieses Projekt jede der zehn Fragen zu sich selbst beantworten kann — Korpus (#41), Kreuzvalidierung (EVALS.md), Zählregel (`count_signals.py`), Präpass (#69/#23), Control Set (adr/0003), Threshold (SCORE-GOVERNANCE.md), Determinismus (L1, EVALS.md), In-Sample-Regel (#85), known-FN-Register, Konfusionsmatrix. Ein Kriterium, das der Autor selbst nicht erfüllt, gehört nicht in die Liste.

## Referenzen

- Weber-Wulff, S., et al. (2023): *Testing of detection tools for AI-generated text*. International Journal for Educational Integrity 19:26 — 14 Tools, alle <80 % Akkuratesse, instabil zwischen Läufen.
- Liang, W., et al. (2023): *GPT detectors are biased against non-native English writers*. Patterns 4(7) — Bias-Beispiel: FP-Raten ungleich verteilt über Autorengruppen; Grund für Frage 5 (Hard Negatives mit Personen-Vielfalt).
- docs/research/deep-dive-slopbeth-unslop-2026-09-05.md (#39) — Marktvergleich: Wettbewerber ohne publizierte Korpora oder Zählregeln.
