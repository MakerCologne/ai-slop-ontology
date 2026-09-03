# Slop-Lexikon

> Single Source of Truth: `lexikon/entries/*.yaml` — diese Datei
> ist ein Build-Artifakt (`scripts/build_lexikon.py`). Nicht von
> Hand editieren.

## Binary-Contrast

`LEX-2026-003` · Kategorie: pattern · Status: stable · v1 · content_hash: `4636a65373fc6bbb`

Rhetorisches Muster "This is not X. It's Y." / "The question isn't X, it's Y." / "It's not just X but Y." — eine kontrastierende Schein-Präzisierung, die KI-Texte auffällig häufig als Pseudo-Insight einsetzen. Lokal seit v1.x als rhetorisches Muster (rhetorical_patterns.py, _BINARY_CONTRAST) erkannt.

*Aliase:* not-X-but-Y, false dichotomy phrase, It's not X, it's Y

**Belegte Aussagen:**
1. petergyang/no-ai-slop listet Binary contrasts als erstes seiner 25 Patterns mit den drei Nennformen "This is not X. It's Y." / "The question isn't X, it's Y." / "It's not just X but Y." und der Umschreib-Empfehlung "→ The eval matters more than the model."
   > „1. **Binary contrasts** — „This is not X. It's Y." / „The question isn't X, it's Y." / „It's not just X but Y." → „The eval matters more than the model."“
   > — <https://github.com/petergyang/no-ai-slop> (Zugriff 2026-08-24)
2. Die lokale Ontology implementiert das Muster in rhetorical_patterns.py (_BINARY_CONTRAST, 4 Regexes), die alle drei bei petergyang genannten Formen covern (Volltext-Verifikation Deep-Dive 02).
   > „Binary contrast | **VORHANDEN** | `rhetorical_patterns.py` `_BINARY_CONTRAST` (4 Regexes; covern petergyangs 3 Nennformen)“
   > — <https://github.com/hikaman/ai-slop-ontology> (Zugriff 2026-08-25)

*Detect:* regex-basiert

*Gegenmaßnahme:* Direkte Aussage mit Komparativ statt Kontrast-Gerüst („X matters more than Y").
*Keep when:* Echte, inhaltsvolle Gegenüberstellung mit beidseitiger Substanz.

*Siehe auch:* Throat-Clearing, Human-Voice

## Ethnopluralismus

`LEX-2026-008` · Kategorie: type · Status: nursery · v1 · content_hash: `2bd3e511dcff0b3f`

Ideologische Strategie, die Kulturen als gleichwertig UND unverträglich erklärt und daraus getrennte, möglichst homogene Räume als einzige operationale Policy ableitet. Modelliert nicht als Schlagwort, sondern als Strategie (Ziel, Taktik, semantische Tarnung), weil genau die Schlussform — von „Differenz“ auf Trennung — den Slop-Charakter erzeugt: endlose „Differenz“-Prosa ohne operationalisierbaren Gehalt außer Trennung (Detektionszweck, keine politische Wertung über den analytischen Bedarf hinaus).

*Aliase:* Ethnopluralism, droit à la différence, Ethno-Differentialismus, Recht auf Differenz

**Belegte Aussagen:**
1. Genealogie: Die moderne Form geht auf Alain de Benoist / Nouvelle Droite / GRECE zurück („droit à la différence“, Ethno-Differentialismus), mit Vorläufern im französischen Neonationalismus der 1950/60er; die Identitäre Bewegung ist die Aktivierungsform, in Deutschland über Kubitschek/IBD in AfD-Nähe.
   > „Der Ethnopluralismus ist eine rechtsextreme Ideologie, die von der Neuen Rechten um Alain de Benoist entwickelt wurde … demnach dürften Kulturen nicht vermischt werden; jede Kultur habe „das Recht auf Differenz“.“
   > — <https://de.wikipedia.org/wiki/Ethnopluralismus> (Zugriff 2026-09-02)
   > „Ethnopluralismus bezeichnet eine völkisch-radikalisierte Variante des Rassismus, die nicht auf eine Hierarchie der „Rassen“, sondern auf die strikte Trennung der Ethnien zielt.“
   > — <https://www.bpb.de/themen/rechtsextremismus/dossier-rechtsextremismus/526659/ethnopluralismus/> (Zugriff 2026-09-02)
2. Strategischer Kern (Taguieff, Rueda, Spektorowski): kein Verzicht auf Exklusion, sondern Rebranding vom biologistischen zu kulturalistischem Rassismus („cultural turn“) — Sprache von Diversität, Antitotalitarismus, Antiimperialismus und Umweltschutz wird gekapert; Taguieff beschreibt die Tarnung suprematistischer Gehalte hinter egalitärem Vokabular.
   > „Strategischer Kern (Taguieff, Rueda, Spektorowski). Kein Verzicht auf Exklusion, sondern Rebranding: biologistischer Rassismus → kulturalistischer Rassismus („cultural turn"). Sprache von Diversität, Antitotalitarismus, Antiimperialismus, Umweltschutz wird gekapert. Taguieff: Tar…“
   > — <https://github.com/MakerCologne/ai-slop-ontology/issues/94> (Zugriff 2026-09-02)
3. Ambiguity-Befund (Journal of Political Ideologies 2023/25): Texte von Benoist, Faye, Eichberg und Lichtmesz zeigen den Cultural Turn bei gleichzeitig fortbestehenden biologistischen Resten — die Doppelbödigkeit ist Design, nicht Nebeneffekt. Malik: Kultur wird zum Synonym für Abstammung, sobald Zugehörigkeit an Herkunftsort und Deszendenz gebunden wird.
   > „Ambiguity-Befund (Journal of Political Ideologies 2023/25). Texte von Benoist, Faye, Eichberg, Lichtmesz: Cultural Turn ja, Reste biologistischer Argumentation bleiben — die Doppelbödigkeit ist Design.“
   > — <https://github.com/MakerCologne/ai-slop-ontology/issues/94> (Zugriff 2026-09-02)
4. Metapolitik: Gramsci von rechts — kulturelle Hegemonie vor Staat. Deshalb wirkt der Begriff als Slop-Generator: Er produziert endlose „Differenz“-Prosa ohne operationalisierbare Policy außer Trennung/Remigration.
   > „Metapolitik. Gramsci von rechts: kulturelle Hegemonie vor Staat. Deshalb taugt der Begriff als Slop-Generator — er produziert endlos „Differenz“-Prosa ohne operationalisierbare Policy außer Trennung/Remigration.“
   > — <https://github.com/MakerCologne/ai-slop-ontology/issues/94> (Zugriff 2026-09-02)

*Detect:* Schluss von „Differenz“/„Vielfalt“ auf getrennte Räume oder Remigration, ökologische Mimikry (Biodiversität ↔ Völkervielfalt), „Recht auf Differenz“ als Politikforderung statt Ethnografie

*Gegenmaßnahme:* Detect-only named evidence (Pattern EthnopluralistRebrand, #92); kein Score. Kennzeichen ist die Schlussform, nicht das Wort: Ethnografische Differenzbeschreibung ohne Segregationsforderung bleibt Hard-Negative.

*Keep when:* Ethnografie, Historiografie oder Ideologieforschung, die das Konzept beschreibt, ohne die Trennungspolitik zu fordern

*Siehe auch:* LEX-2026-006, LEX-2026-007, adr/0008, #92, #93, #96

## Human-Slop

`LEX-2026-006` · Kategorie: type · Status: nursery · v1 · content_hash: `c1f24339fcb01a81`

Menschlich verfasster oder menschlich gerahmter Content, der die Slop-Kriterien erfüllt (Template, Informationsgewinn nahe null, geringe Falsifizierbarkeit, Push-Distribution), ohne KI-Autorschaft. Schwesterklasse zu SyntheticContent; Slop wird als Risikoprofil, nicht als Autorschaftsklasse verstanden (adr/0008). Detect-only bis zur Korpus-Reife (#98).

*Aliase:* menschlicher Slop, HumanSlopCandidate

**Belegte Aussagen:**
1. Die Slop-Prototypen (Superficial Competence, Asymmetric Effort, Mass Producibility) beschreiben auch menschlichen Output, sobald Sorgfalt/Verifikation fehlen und Distribution Push ist — Grundlage des Epics #89 und der HumanSlop-Kandidatenklasse.
   > „Befund: Willisons drei Bedingungen und Kommers' Prototypen (Superficial Competence, Asymmetric Effort, Mass Producibility) beschreiben auch menschlichen Output, sobald Sorgfalt/Verifikation fehlen und Distribution Push ist.“
   > — <https://github.com/MakerCologne/ai-slop-ontology/issues/89> (Zugriff 2026-09-02)
2. Der Detector bleibt Detector (adr/0001) und neue Module sind default detect-only (adr/0006) — Human-Slop-Signale dürfen nicht zu einer Gesinnungsnote werden; Hard-Negatives sind Pflicht (adr/0005).
   > „Score-Gate auf politische Sprache → Detector wird Zensor (Verstoß gegen adr/0001). ... adr/0005: kein Benchmark-Gaming; Hard-Negatives Pflicht.“
   > — <https://github.com/MakerCologne/ai-slop-ontology/issues/90> (Zugriff 2026-09-02)

*Detect:* Totalerklärung ohne Einzelfall, Herkunft als Kollektivschuld, unfalsifizierbare Deutungsschablone, Erlöser-Schema

*Gegenmaßnahme:* detect-only named evidence; kein slop_score-Beitrag vor
*Keep when:* Policy-Argument mit Akteur, Instrument, Beleg; Statistik mit Nenner, Zeitraum, Quelle; klar markierte Satire

*Siehe auch:* LEX-2026-007, adr/0008, #93

## Human-Voice

`LEX-2026-005` · Kategorie: counter · Status: beta · v1 · content_hash: `8ca8b1ee5819cc8a`

Counter-Prinzip: Detektion von Slop ist nur "half the job" — das positive Ziel ist eine erkennbare menschliche Stimme. Sechs Soul-Prinzipien (Meinung haben, Rhythmus variieren, Komplexität anerkennen, Ich-Form erlauben, kontrolliertes Chaos, Konkretheit) wirken der sterilen, voiceless-Glättung entgegen, die selbst ein Slop-Signal ist (Over-Sanitization).

*Aliase:* adding soul, soul principles, positive Gegenprofil

**Belegte Aussagen:**
1. potetos "unslop"-Skill (in poteto/noodle) etabliert "Adding soul" als positives Gegenprogramm nach dem Pattern-Removal: "Removal ist nur half the job, sterile, voiceless writing is just as obvious" — mit Prinzipien wie "Have opinions", "Vary rhythm", "Acknowledge complexity", "Use 'I' when it fits".
   > „„Adding soul" 🆕 (positives Gegenprogramm — Removal ist nur „half the job", „sterile, voiceless writing is just as obvious"): „Have opinions. React to facts instead of neutrally listing pros and cons." / „Vary rhythm. Short sentences. Then longer ones that take their time. Mix it …“
   > — <https://www.skills.sh/poteto/noodle/unslop> (Zugriff 2026-08-24)
2. Die lokale Ontology hat diese Prinzipien als references/human-voice.md übernommen (Issue #21, Batch G); der 4-Schritt-Prozess des Skills endet mit einem iterativen Self-Audit: "What makes this obviously AI generated?" — Fix remaining tells.
   > „Prozess (4 Schritte): 1. Scan für Patterns → 2. „Rewrite — preserve meaning, match intended tone" → 3. „Add soul (see next section)" → 4. Self-Audit: „What makes this obviously AI generated?" Fix remaining tells.“
   > — <https://github.com/hikaman/ai-slop-ontology> (Zugriff 2026-08-25)

*Gegenmaßnahme:* Redaktionelle Zielperspektive neben der Detektion: Meinungen, Rhythmus- Variation, erste Person, konkrete Details statt neutraler Auflistung.

*Keep when:* Nicht anwendbar (Gegenprinzip, kein Detektionssignal).

*Siehe auch:* Binary-Contrast

## Ideological-Slop

`LEX-2026-007` · Kategorie: type · Status: nursery · v1 · content_hash: `ec6e17c1036a4398`

Untertyp von Human-Slop: ritualhafte ideologische Prosa, die einen Frame reproduziert, ohne Informationsgewinn zu erzeugen — Totalerklärungen, Kollektivzuweisungen, Erlöser-Schemata, unfalsifizierbare Deutungsschablonen. Abgegrenzt zum Policy-Argument: Dieses nennt Akteur, Instrument und Beleg und ist falsifizierbar. Umsetzung als detect-only Rhetorik-Layer (#92); Ontologie-Klasse in der Extension (#93).

*Aliase:* IdeologicalSlop, Ritualprosa, Ritual-Frame

**Belegte Aussagen:**
1. Option B (detect-only Rhetorik-Layer) ist der kleinste Schritt, der das Phänomen messbar macht, ohne den Detector zum Gesinnungsscanner zu machen; Option A (Ontologie-Klasse mit Score) folgt nur nach Opt-in und Korpus-Reife — Empfehlung des bewerteten Vorschlags in #91/adr/0008.
   > „B ist der kleinste Schritt, der das Phänomen messbar macht, ohne den Detector zum Gesinnungsscanner zu machen. A ist der Schritt, der das Phänomen denkbar macht — aber nur, wenn #86 und das neue ADR denselben Satz sagen: Slop ist ein Risikoprofil, keine Autorschaftsklasse.“
   > — <https://github.com/MakerCologne/ai-slop-ontology/issues/91> (Zugriff 2026-09-02)
2. Ein ideologischer Frame wirkt als Slop-Generator über Metapolitik: Er produziert endlose Frame-Prosa ohne operationalisierbare Policy außer Trennung — Beispiel Ethnopluralismus (#94).
   > „Metapolitik. Gramsci von rechts: kulturelle Hegemonie vor Staat. Deshalb taugt der Begriff als Slop-Generator — er produziert endlos „Differenz"-Prosa ohne operationalisierbare Policy außer Trennung/Remigration.“
   > — <https://github.com/MakerCologne/ai-slop-ontology/issues/94> (Zugriff 2026-09-02)

*Detect:* jedes Ereignis bestätigt denselben Frame, Schluss von Differenz auf Trennung

*Gegenmaßnahme:* named evidence mit zitiertem Beleg; kein Score
*Keep when:* Konkretes Verfahren (Ausschuss, Verbot, Minderheitsregierung), Einzelclaim mit Testbedingung, Statistik mit Nenner/Zeitraum/Quelle

*Siehe auch:* LEX-2026-006, adr/0008, #92, #93

## Marketing-CTA

`LEX-2026-004` · Kategorie: pattern · Status: beta · v1 · content_hash: `be4238b67f8349de`

Marketing- und Conversion-Phrasen ("start your free trial today", "book a demo", "trusted by startups and enterprises alike"), die in KI-generiertem Marketing- und Produktext gehäuft auftreten. In der lokalen Ontology als phrase-Kategorie marketing_cta umgesetzt (Issue-Batch F, 20 Phrasen mit Korpus-Belegen).

*Aliase:* marketing_cta, SaaS-CTA-Phrasen

**Belegte Aussagen:**
1. Die 20 marketing_cta-Phrasen der lokalen Ontology wurden aus dem FN-Korpus extrahiert und mit Trefferzahlen belegt, z. B. "start your free trial today" (12 slop-Texte), "book a demo" (8), "trusted by startups and enterprises alike" (12), "all in one place" (16) — je 0 Clean-Treffer.
   > „start your free trial today. Most Popular Book a demo with our team. What does this mean for your team? The short answer is yes. [...] But here's the catch: the API rate-limits you anyway.“
   > — <https://github.com/hikaman/ai-slop-ontology/blob/main/eval/corpus.jsonl> (Zugriff 2026-08-25)
2. Der unabhängige Review (review-batch-f.md) bestätigt die echten LLM-/CTA-Artefakte als "hohe Portabilität — starke Signale", warnt aber zugleich vor generischen marketing_cta/report_hedging-Phrasen als Haupt-FP-Risiko in menschlicher Arbeitsprosa.
   > „„start your free trial today", „trusted by startups and enterprises alike", „99.9% uptime" [...] | **echte LLM-/CTA-Artefakte**, hohe Portabilität — starke Signale“
   > — <https://github.com/hikaman/ai-slop-ontology> (Zugriff 2026-08-25)

*Detect:* regex-basiert

*Gegenmaßnahme:* Konkrete, belegte Produktaussagen statt Conversion-Formeln.
*Keep when:* Echte Landingpage/CTA-Kontexte, in denen die Handlungsaufforderung der Zweck des Textes ist.

*Siehe auch:* Throat-Clearing

## Provenance-Marker

`LEX-2026-002` · Kategorie: signal · Status: stable · v1 · content_hash: `601bd6adbd64e27b`

Deterministische Artefakte KI-generierter Texte aus der Tool-Interaktion — z. B. ":contentReference[oaicite:N]{index=N}", "turn0search0" (mit Private-Use-Area-Unicode umgeben), "oai_citation" oder nackte PUA-Ziffern. Nahezu false-positive-frei und per Regex maschinell nachweisbar.

*Aliase:* oaicite, turn0search0, contentReference, PUA-Ziffern, interne Formatierungs-Bugs

**Belegte Aussagen:**
1. Wikipedia "Signs of AI writing" dokumentiert diese Marker als interne Formatierungs-Bugs von ChatGPT und bezeichnet sie als "unambiguous" — ChatGPT: ":contentReference[oaicite:N]{index=N}", "Example+1", "oai_citation", "turn0search0" (mit PUA-Unicode umgeben; Zähler steigt durch den Text).
   > „Interne Formatierungs-Bugs (unambiguous!) — ChatGPT: `:contentReference[oaicite:N]{index=N}`, `Example+1`, `oai_citation`, `turn0search0` (mit PUA-Unicode umgeben; Zähler steigt durch Text)“
   > — <https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing> (Zugriff 2026-08-24)
2. Die lokale Ontology hat diese Marker mit Issue #20 als deterministische Provenance-Signale übernommen (Batch A, burn-batch-a.md); Deep-Dive 03 stufte sie als "stärkstes Einzelsignal der ganzen Wiki-Seite" mit Konfidenz ≈1.0 ein.
   > „Deterministische Provenance-Marker (§3.4/Punkt 29): `turn0search0`+PUA-Ziffern, `oaicite`, `2025-XX-XX`, `PASTE_*_HERE` — die lokal komplett fehlen, obwohl sie die höchste mögliche Konfidenz (≈1.0) haben“
   > — <https://github.com/hikaman/ai-slop-ontology> (Zugriff 2026-08-25)

*Detect:* regex-basiert

*Gegenmaßnahme:* Zitations-Artefakte entfernen und Belege sauber formatieren.
*Keep when:* Nie legitim — Vorkommen ist immer ein Tool-Artefakt.

*Siehe auch:* Throat-Clearing

## Throat-Clearing

`LEX-2026-001` · Kategorie: pattern · Status: stable · v1 · content_hash: `6353708f973c4676`

Gesprochene Aufwärm-Phrasen ("Here's the thing:", "It turns out", "Let me be clear"), die den Punkt aufschieben statt ihn zu machen — ein hochfrequentes KI-Text-Signal auf Phrase-Ebene.

*Aliase:* throat clearing openers, faux-candid openings

**Belegte Aussagen:**
1. stop-slop führt 15 Throat-Clearing-Opener explizit als Cut-Kandidaten, darunter "Here's the thing:", "The uncomfortable truth is" und "It turns out", plus die generische Regel "Any 'here's what/this/that' construction is throat-clearing before the point."
   > „Throat-Clearing Openers (15): „Here's the thing:" · „Here's what [X]" · „Here's this [X]" · „Here's that [X]" · „Here's why [X]" · „The uncomfortable truth is" · „It turns out" · „The real [X] is" · „Let me be clear"“
   > — <https://github.com/hardikpandya/stop-slop> (Zugriff 2026-08-24)
2. Wikipedia "Signs of AI writing" listet Fake-candid openings derselben Familie ("Honestly?", "Look,", "Here's the thing", "The thing is") als eigenständiges Anzeichen KI-generierten Texts.
   > „Fake-candid openings — „Honestly?", „Look,", „Here's the thing", „The thing is", „Let me be honest", „Real talk" — als standalone hooks“
   > — <https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing> (Zugriff 2026-08-24)

*Detect:* here's-what/this/that-Konstruktion vor dem eigentlichen Punkt

*Gegenmaßnahme:* Direkt mit dem Punkt beginnen; Opener streichen (Minimum-Effective-Edit).
*Keep when:* In echter zitierter Rede oder als bewusstes Stilmittel mit Inhalt.

*Siehe auch:* Binary-Contrast, Marketing-CTA

