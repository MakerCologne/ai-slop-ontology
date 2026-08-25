# DE-Coverage — Mapping des DE-Pattern-Katalogs (Issue #76, Teil 1)

**Status:** Teil 1 (Quick Wins M46/M47/M48/M49 implementiert) · **Datum:** 2026-08-25
**Referenz-Katalog:** humanizer-de v5.22.2 `references/patterns.md` — **72 nummerierte Muster** (der im Deep-Dive genannte „82er-Katalog" zählt offenbar Überschriften/Sektionen mit; die Kurzreferenz listet exakt 72 Zeilen — Claim-Korrektur dokumentiert).
**Lizenz-Schutz:** Der Referenz-Katalog steht teilweise unter CC BY-SA 4.0 (Wikipedia-abgeleitetes Pattern-Material). Dieses Mapping beschreibt jedes Muster **in eigenen Worten** als Konzept (Kurzname + Zuordnung zu unseren Signalen); es werden **keine Pattern-Listen, Regexes oder Beispielsätze übernommen**. Die Quick-Win-Implementierung `skills/ai-slop-detection/scripts/de_typography.py` ist eine Eigen-Ableitung aus de.wikipedia „Anzeichen für KI-generierte Inhalte" + eigenen DE-Beispielen.
**Quellen-Konzepte:** de.wikipedia „Anzeichen für KI-generierte Inhalte", en.wikipedia „Signs of AI writing" (beide bereits Grundlage unserer #7/#17-Signale).

## Legende

- **GEDECKT** — Konzept UND Match-Daten existieren bereits bei uns (meist EN; Deckung greift sprachagnostisch, z. B. Unicode-/Struktur-Signale).
- **DE-VARIANTE** — Konzept existiert (Signal/Modul vorhanden), aber die Match-Daten sind EN; deutsche Entsprechungen fehlen → Layer-Aufbau via **#77** (DE-Phrase-Datenbank in ontology.json).
- **NEU** — weder Konzept noch DE-Daten bei uns vorhanden → Kandidaten für Folge-Issues (Priorisierung unten).

## Mapping (M1–M72)

| M# | Konzept (eigene Worte) | Status | Unsere Deckung / Ziel |
|---|---|---|---|
| M1 | Symbolik-Betonung („steht als Zeugnis für") | DE-VARIANTE | metaphor_abuse (EN) → #77 |
| M2 | Werbesprache/Superlative | DE-VARIANTE | Buzzword-Tiers (EN) → #77 |
| M3 | Meta-Kommentare statt Inhalt | DE-VARIANTE | meta_commentary (EN) → #77 de_meta_comment |
| M4 | Mechanische Konjunktionen (ferner, darüber hinaus) | DE-VARIANTE | generic_transitions (EN) → #77 |
| M5 | Abschnitts-Zusammenfassungen | DE-VARIANTE | closing_formulas/Recap (EN) → #77 |
| M6 | Unpassendes „Fazit"-Kapitel | NEU (klein) | structural: Fazit-Heading ohne Substanz |
| M7 | Dichotom-Schluss + Lob→Herausforderung→Ausblick-Schablone | DE-VARIANTE | BinaryContrast #26 + mirrored intro↔conclusion → DE-Daten |
| M8 | Negativ-Parallelismen (nicht nur … sondern auch) | DE-VARIANTE | _BINARY_CONTRAST #26 → DE-Phrasen |
| M9 | Regel-der-Drei-Aufzählungen | GEDECKT | rhetorical_patterns (forced triads) |
| M10 | Partizip-I-Anhängsel („…gewährleistend") | NEU | DE-Grammatik-Signal, Kandidat Folge-Batch |
| M11 | Vage Autoritäten | DE-VARIANTE | authority_claims/weasel_attribution → #77 de_authority_floskel |
| M12 | Schein-Reichweite („von traditionell bis modern") | DE-VARIANTE | micro_patterns FalseRange → DE-Endpoints |
| M13 | Übermäßige Fettschrift | GEDECKT | formatting slop (rhetorical_patterns) |
| M14 | Falsche Listen-Syntax | GEDECKT | markup_anomalies |
| M15 | Emojis vor Überschriften | GEDECKT | markup_anomalies/formatting slop |
| M16 | Gedankenstrich-Cluster | GEDECKT | EmDashExcess + Em-Dash-Doctrine |
| M17 | Briefartiger Aufbau (Betreff/Anrede/Grußformel) | NEU (klein) | Kandidat instruction/provenance-Umfeld |
| M18 | Kollaborativ-Floskeln („Ich hoffe, das hilft") | DE-VARIANTE | chatbot leftovers (EN) → #77 |
| M19 | Wissensgrenzen-Hinweise („Stand …") | GEDECKT | provenance #20 (Update-Marker) |
| M20 | Prompt-Ablehnungsreste | GEDECKT | provenance #20 / instruction slop |
| M21 | Platzhaltertext ([Name einfügen]) | GEDECKT | markup_anomalies/proof_metrics |
| M22 | Such-Links statt Referenzen | GEDECKT | provenance #20 (Pseudo-Quellen) |
| M23 | Markdown statt Zielformat | GEDECKT | markup_anomalies |
| M24 | KI-Tool-Artefakte (oaicite, contentReference) | GEDECKT | provenance #20 (Konfidenz ≈1.0) |
| M25 | Defekte Links | GEDECKT (Teil) | provenance #20; Link-Prüfung Out-of-scope offline |
| M26 | Zitat-/Quellenfabrikation | DE-VARIANTE | proof_metrics + Validierung → DE-Zitate |
| M27 | Falsches Referenz-/Datumsformat | GEDECKT (Teil) | de_typography M48 (DE-Seite) |
| M28 | Falsche Wiki-Kategorien | NEU (wiki-spezifisch) | out of scope (Plattform-) |
| M29 | Abbruch mittendrin | NEU (klein) | Kandidat structural |
| M30 | Stilwechsel zwischen Absätzen | DE-VARIANTE | register_drift #81 → DE-Marker |
| M31 | Ich-Form-Bearbeitungszusammenfassungen | NEU (verhaltensbasiert) | out of scope (Text-Engine) |
| M32 | Autoritäts-Floskeln („die eigentliche Frage ist") | DE-VARIANTE | rhetorical_setups/authority → #77 |
| M33 | Signposting/Ankündigungen | DE-VARIANTE | rhetorical_setups → #77 |
| M34 | Fragment-Überschriften (Einzeiler-Nachspann) | DE-VARIANTE | rhythm/kicker-Signale → DE |
| M35 | Rhetorische Fragen als Fake-Dialog | DE-VARIANTE | rhetorical_patterns → #77 |
| M36 | Universal-Geschichts-Eröffnung („Seit jeher") | DE-VARIANTE | opening_formulas → #77 |
| M37 | „In der heutigen X-Welt"-Rahmung | DE-VARIANTE | opening_formulas + multilingual-DE-Buzzwords (bereits teilweise in ontology.json) → Ausbau #77 |
| M38 | Aspirativer Schluss (grenzenlose Möglichkeiten) | DE-VARIANTE | closing_formulas/trailing moral → #77 |
| M39 | Passiv-/subjektlose Fragmente | NEU | Kandidat structural (EN+DE messbar) |
| M40 | Wenn-Klausel-Stapel | NEU | Kandidat syntaktisch |
| M41 | Fehlkalibrierte Gewissheit | DE-VARIANTE | hedging_qualifiers → #77 |
| M42 | Beleg-Aussage-Inkongruenz | DE-VARIANTE | proof_metrics (Kontext-Check) → DE |
| M43 | Versteckte Unicode-Zeichen | GEDECKT | input_norm #40 (ZWS/BOM/Bidi) |
| M44 | Standard-Kapitel ohne Substanz | DE-VARIANTE | structural/list_heavy → DE-Heuristik |
| M45 | Calques/False Friends („am Ende des Tages") | → #77 | de_calque (dieser Batch, Teil 2) |
| **M46** | **Falsche deutsche Anführungszeichen** | **GEDECKT (neu)** | **de_typography.quote_mismatch (dieser Batch)** |
| **M47** | **Englische Titel-Großschreibung** | **GEDECKT (neu)** | **de_typography.title_case_headings** |
| **M48** | **Englisches Dezimal-/Datumsformat** | **GEDECKT (neu)** | **de_typography.en_number_formats (Versionen exempt)** |
| **M49** | **Genitiv-Apostroph** | **GEDECKT (neu)** | **de_typography.genitive_apostrophe (Marken-Allowlist)** |
| M50 | Stichpunkt-Großschreibung/Endpunkte | NEU (klein) | Kandidat Typografie |
| M51 | Parataxe-Häufung | NEU | Kandidat syntaktisch |
| M52 | Diff-verankertes Schreiben | NEU | Kandidat provenance/Prosa |
| M53 | Lückenfüllende Spekulation | DE-VARIANTE | hedging → #77 |
| M54 | Doppelpunkt-Titel-Schema | DE-VARIANTE | formatting slop → DE |
| M55 | Gleichförmiger Satzrhythmus | GEDECKT | UniformSentenceLength/Burstiness, Copula #22, Adverb #24 |
| M56 | Aphorismus-Formeln | NEU | Kandidat phrase DE |
| M57 | Markdown-Struktur-Artefakte | GEDECKT | markup_anomalies/formatting slop |
| M58 | Abstrakta-Stapel/Nominalstil | NEU (Teil) | Density-Dimension streift; Kandidat DE |
| M59 | Forcierte Ich-Lockerheit | DE-VARIANTE | faux-candid (EN, rhetorical) → #77 |
| M60 | Synonym-Rotation für Entitäten | NEU | sprachagnostisch messbar (Entity-Variationsrate) — Priorität |
| M61 | Isometrisches Dokument (gleich lange Einheiten) | NEU | sprachagnostisch (Varianz je Struktureinheit) — Priorität |
| M62 | Bewertender Schluss-Satz ohne neue Info | NEU | verwandt TrailingMoral |
| M63 | Modalpartikel-Anomalie | OFFEN (Stub) | naturalness_guard.modal_particle_anomaly = Stub; DE-Inventar folgt (s. #81) |
| M64 | KI-Marker-Vokabular DE | → #77 | de_ai_vocab (dieser Batch, Teil 2) |
| M65 | Kopula-Vermeidung („fungiert als") | DE-VARIANTE | copula_rate #22 → DE-Verben |
| M66 | Fake-Analyse-Anhang (Relativsatz ohne Info) | NEU | sprachagnostisch schwer; Kandidat |
| M67 | Ankündigungs-Spaltsatz („Was mich überraschte …") | NEU | Kandidat DE Syntax |
| M68 | Komparativ-Rahmung („weniger X als vielmehr Y") | NEU | Kandidat phrase DE |
| M69 | Struktureller Register-Kollaps | DE-VARIANTE | register_drift #81 → DE-Profile |
| M70 | Falsche Agency abstrakter Subjekte | DE-VARIANTE | micro_patterns FalseAgency → DE-Subjekte/Verben |
| M71 | Retroaktive Scheinnuance („Genauer gesagt …") | NEU | Kandidat phrase DE |
| M72 | Pseudo-therapeutische Validierung | NEU | Konversations-Kontext, Kandidat |

## Bilanz (Teil 1)

- **GEDECKT (bestehend):** 20 Muster (M9, M13–M16, M19–M25 (Teil), M43, M55, M57)
- **GEDECKT (neu, dieser Batch):** 4 Muster (M46, M47, M48, M49) — `de_typography.py`, detect-only, DE-Sprachgate, je 3/3/2 Fixtures (tests/test_de_typography.py)
- **DE-VARIANTE (→ #77-Layer):** 30 Muster — Phrase-Datenbank-Ausbau (de_calque, de_ai_vocab, de_authority_floskel, de_meta_comment als erste vier Kategorien)
- **NEU:** 18 Muster — davon sprachagnostisch priorisiert: M60 (Synonym-Rotation), M61 (Isometrie); Rest als Kandidaten-Register für Folge-Batches
- **OFFEN (Stub):** M63 Modalpartikel-Anomalie — bewusst Stub bis DE-Inventar steht (#81-Entscheidung)

Kein Muster wird als „automatisch fixbar" behandelt — alle DE-Signale sind detect-only/advisory (Anti-Auto-Rewrite-Disziplin, vgl. SIGNAL-DOD.md).
