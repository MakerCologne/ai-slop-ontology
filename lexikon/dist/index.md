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

