# DE-Coverage — Mapping des DE-Pattern-Katalogs (Issue #76, Teil 1+2)

**Status:** Teil 1 (Quick Wins M46–M49) · **Teil 2** (12 neue de_*-Phrase-Kategorien + M60/M61-Strukturmodul `structure_metrics.py`, je Signal 3/3/2-Fixtures; Evidence je Phrase nach RI-1/RI-2: Wikipedia-Projektseite MIT Namespace-Präfix oder own:-Beleg, ≥2 Belege als FU offen) · **Datum:** 2026-08-25
**Referenz-Katalog:** humanizer-de v5.22.2 `references/patterns.md` — **72 nummerierte Muster** (der im Deep-Dive genannte „82er-Katalog" zählt offenbar Überschriften/Sektionen mit; die Kurzreferenz listet exakt 72 Zeilen — Claim-Korrektur dokumentiert).
**Lizenz-Schutz:** Der Referenz-Katalog steht teilweise unter CC BY-SA 4.0 (Wikipedia-abgeleitetes Pattern-Material). Dieses Mapping beschreibt jedes Muster **in eigenen Worten** als Konzept (Kurzname + Zuordnung zu unseren Signalen); es werden **keine Regexes oder Beispielsätze übernommen**. Bei den Phrase-Items gilt: Einzelne Formulierungen, die wortgleich auf der de-Wikipedia-Projektseite „Wikipedia:Anzeichen für KI-generierte Inhalte“ stehen, sind dieser Primärquelle attribuiert (die Wikipedia nennt sie selbst; der Referenz-Katalog ist Ko-Derivat) — Wortgleichheit mit dem Referenz-Katalog allein ist kein Beleg und wird mit `own:`-Belegen vermieden (vgl. RJ-1-Fixup). Die Quick-Win-Implementierung `skills/ai-slop-detection/scripts/de_typography.py` ist eine Eigen-Ableitung aus derselben Wikipedia-Seite + eigenen DE-Beispielen.
**Quellen-Konzepte:** de.wikipedia „Anzeichen für KI-generierte Inhalte", en.wikipedia „Signs of AI writing" (beide bereits Grundlage unserer #7/#17-Signale).

## Legende

- **GEDECKT** — Konzept UND Match-Daten existieren bereits bei uns (meist EN; Deckung greift sprachagnostisch, z. B. Unicode-/Struktur-Signale).
- **DE-VARIANTE** — Konzept existiert (Signal/Modul vorhanden), aber die Match-Daten sind EN; deutsche Entsprechungen fehlen → Layer-Aufbau via **#77** (DE-Phrase-Datenbank in ontology.json).
- **NEU** — weder Konzept noch DE-Daten bei uns vorhanden → Kandidaten für Folge-Issues (Priorisierung unten).

## Mapping (M1–M72)

| M# | Konzept (eigene Worte) | Status | Unsere Deckung / Ziel |
|---|---|---|---|
| M1 | Symbolik-Betonung („steht als Zeugnis für") | **GEDECKT (neu, T2)** | **de_symbolik (Teil 2)** | |
| M2 | Werbesprache/Superlative | **GEDECKT (neu, T2)** | **de_superlativ (Teil 2)** | |
| M3 | Meta-Kommentare statt Inhalt | DE-VARIANTE | meta_commentary (EN) → #77 de_meta_comment |
| M4 | Mechanische Konjunktionen (ferner, darüber hinaus) | **GEDECKT (neu, T2)** | **de_transitions (Teil 2)** | |
| M5 | Abschnitts-Zusammenfassungen | **GEDECKT (neu, T2)** | **de_recap (Teil 2)** | |
| M6 | Unpassendes „Fazit"-Kapitel | **GEDECKT (neu, #76-Rest M6 19.09.)** | **structure_metrics.hollow_conclusion (≤20 Wörter Körper ohne Zahlen/Verweise, detect-only, conf 0.5)** |
| M7 | Dichotom-Schluss + Lob→Herausforderung→Ausblick-Schablone | **GEDECKT (neu, #77-Rest W5 13.09.)** | **de_dichotomy_close (Voll-Zweibeleg de-ev-23)** | |
| M8 | Negativ-Parallelismen (nicht nur … sondern auch) | **GEDECKT (neu, T2)** | **de_binary_contrast (Teil 2)** | |
| M9 | Regel-der-Drei-Aufzählungen | GEDECKT | rhetorical_patterns (forced triads) |
| M10 | Partizip-I-Anhängsel („…gewährleistend") | **GEDECKT (neu, T2)** | **de_participle (Teil 2, Phrase-Layer)** | |
| M11 | Vage Autoritäten | **GEDECKT (neu, T2)** | **de_authority_floskel (#77) + de_vague_authority (T2, disjunkt)** | |
| M12 | Schein-Reichweite („von traditionell bis modern") | **GEDECKT (neu, T2)** | **de_false_range (Teil 2)** | |
| M13 | Übermäßige Fettschrift | GEDECKT | formatting slop (rhetorical_patterns) |
| M14 | Falsche Listen-Syntax | GEDECKT | markup_anomalies |
| M15 | Emojis vor Überschriften | GEDECKT | markup_anomalies/formatting slop |
| M16 | Gedankenstrich-Cluster | GEDECKT | EmDashExcess + Em-Dash-Doctrine |
| M17 | Briefartiger Aufbau (Betreff/Anrede/Grußformel) | NEU (klein) | Kandidat instruction/provenance-Umfeld |
| M18 | Kollaborativ-Floskeln („Ich hoffe, das hilft“) | **GEDECKT (neu, #77-Rest 13.09.)** | **de_chatbot_leftover (Voll-Zweibeleg de-ev-17)** |
| M19 | Wissensgrenzen-Hinweise („Stand …") | GEDECKT | provenance #20 (Update-Marker) |
| M20 | Prompt-Ablehnungsreste | GEDECKT | provenance #20 / instruction slop |
| M21 | Platzhaltertext ([Name einfügen]) | GEDECKT | markup_anomalies/proof_metrics |
| M22 | Such-Links statt Referenzen | GEDECKT | provenance #20 (Pseudo-Quellen) |
| M23 | Markdown statt Zielformat | GEDECKT | markup_anomalies |
| M24 | KI-Tool-Artefakte (oaicite, contentReference) | GEDECKT | provenance #20 (Konfidenz ≈1.0) |
| M25 | Defekte Links | GEDECKT (Teil) | provenance #20; Link-Prüfung Out-of-scope offline |
| M26 | Zitat-/Quellenfabrikation | **GEDECKT (neu, #77-Rest W5 13.09.)** | **de_quote_fabrication (Voll-Zweibeleg de-ev-24)** | |
| M27 | Falsches Referenz-/Datumsformat | GEDECKT (Teil) | de_typography M48 (DE-Seite) |
| M28 | Falsche Wiki-Kategorien | NEU (wiki-spezifisch) | out of scope (Plattform-) |
| M29 | Abbruch mittendrin | NEU (klein) | Kandidat structural |
| M30 | Stilwechsel zwischen Absätzen | **GEDECKT (neu, #77-Rest W5 13.09.)** | **de_register_shift (Voll-Zweibeleg de-ev-25)** | |
| M31 | Ich-Form-Bearbeitungszusammenfassungen | NEU (verhaltensbasiert) | out of scope (Text-Engine) |
| M32 | Autoritäts-Floskeln („die eigentliche Frage ist") | **GEDECKT (neu, #77-Rest W6 15.09.)** | **de_rhetorical_setup (Voll-Zweibeleg de-ev-26; disjunkt zu de_authority_floskel)** |
| M33 | Signposting/Ankündigungen | **GEDECKT (neu, #77-Rest 13.09.)** | **de_signposting (Voll-Zweibeleg de-ev-18)** |
| M34 | Fragment-Überschriften (Einzeiler-Nachspann) | DE-VARIANTE | rhythm/kicker-Signale → DE |
| M35 | Rhetorische Fragen als Fake-Dialog | **GEDECKT (neu, #77-Rest 13.09.)** | **de_fake_dialog (Voll-Zweibeleg de-ev-20)** |
| M36 | Universal-Geschichts-Eröffnung („Seit jeher") | **GEDECKT (neu, T2)** | **de_opening (Teil 2)** | |
| M37 | „In der heutigen X-Welt"-Rahmung | **GEDECKT (neu, T2)** | **de_opening + multilingual.german.buzzwords** | |
| M38 | Aspirativer Schluss (grenzenlose Möglichkeiten) | **GEDECKT (neu, T2)** | **de_closing (Teil 2)** | |
| M39 | Passiv-/subjektlose Fragmente | NEU | Kandidat structural (EN+DE messbar) |
| M40 | Wenn-Klausel-Stapel | NEU | Kandidat syntaktisch |
| M41 | Fehlkalibrierte Gewissheit | **GEDECKT (neu, T2)** | **de_hedging (Teil 2)** | |
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
| M53 | Lückenfüllende Spekulation | **GEDECKT (neu, T2)** | **de_hedging (Teil 2, Wissensgrenzen-Hinweise)** | |
| M54 | Doppelpunkt-Titel-Schema | DE-VARIANTE | formatting slop → DE |
| M55 | Gleichförmiger Satzrhythmus | GEDECKT | UniformSentenceLength/Burstiness, Copula #22, Adverb #24 |
| M56 | Aphorismus-Formeln | **GEDECKT (neu, #77-Rest W6 15.09.)** | **de_aphorism (Voll-Zweibeleg de-ev-27)** |
| M57 | Markdown-Struktur-Artefakte | GEDECKT | markup_anomalies/formatting slop |
| M58 | Abstrakta-Stapel/Nominalstil | NEU (Teil) | Density-Dimension streift; Kandidat DE |
| M59 | Forcierte Ich-Lockerheit | **GEDECKT (neu, #77-Rest 13.09.)** | **de_faux_candid (Voll-Zweibeleg de-ev-21)** |
| M60 | Synonym-Rotation für Entitäten | **GEDECKT (neu, T2)** | **structure_metrics.synonym_rotation (detect-only)** | |
| M61 | Isometrisches Dokument (gleich lange Einheiten) | **GEDECKT (neu, T2)** | **structure_metrics.isometry (detect-only)** | |
| M62 | Bewertender Schluss-Satz ohne neue Info | NEU | verwandt TrailingMoral |
| M63 | Modalpartikel-Anomalie | **GEDECKT (neu, #76-Rest M63 19.09.)** | **naturalness_guard.modal_particle_anomaly (DE-Inventar 12 Partikeln, detect-only, conf 0.45; Voll-Zweibeleg: Duden-Grammatik-Referenz REFERENCES.md #40 + own:corpus de-ev-29)** |
| M64 | KI-Marker-Vokabular DE | → #77 | de_ai_vocab (dieser Batch, Teil 2) |
| M65 | Kopula-Vermeidung („fungiert als“) | **GEDECKT (neu, #77-Rest 13.09.)** | **de_copula_avoidance (Voll-Zweibeleg de-ev-19)** |
| M66 | Fake-Analyse-Anhang (Relativsatz ohne Info) | **GEDECKT (neu, #76-Rest)** | **structure_metrics.fake_analysis_appendix (≥2 Treffer, detect-only)** |
| M67 | Ankündigungs-Spaltsatz („Was mich überraschte …") | **GEDECKT (neu, T2)** | **de_announcement_cleft (Teil 2)** | |
| M68 | Komparativ-Rahmung („weniger X als vielmehr Y") | NEU | Kandidat phrase DE |
| M69 | Struktureller Register-Kollaps | DE-VARIANTE | register_drift #81 → DE-Profile |
| M70 | Falsche Agency abstrakter Subjekte | **GEDECKT (neu, #77-Rest 13.09.)** | **de_false_agency (Voll-Zweibeleg de-ev-22)** |
| M71 | Retroaktive Scheinnuance („Genauer gesagt …") | **GEDECKT (neu, #76-Rest)** | **structure_metrics.pseudo_nuance (≥2 Marker, detect-only)** |
| M72 | Pseudo-therapeutische Validierung | **GEDECKT (neu, #77-Rest W6 15.09.)** | **de_therapeutic_validation (Voll-Zweibeleg de-ev-28)** |

## Bilanz (Teil 2, dieser Batch)

- **GEDECKT (neu, T2):** 14 weitere Muster — Phrase-Layer de_transitions, de_recap, de_superlativ, de_symbolik, de_vague_authority, de_participle, de_binary_contrast, de_false_range, de_opening, de_closing, de_hedging, de_announcement_cleft (je 6 Phrasen, conf 0.6, Evidence-Pflicht) + structure_metrics.py (M60 SynonymRotation, M61 IsometricUnits; detect-only, sprachagnostisch, daher bewusst ohne DE-Gate)
- **DE-Signal-Zähler:** Teil 1: 4 (de_typography) + 4 (#77-Kategorien) = 8; Teil 2: +12 Kategorien +2 Struktur = 14 → **22 DE-Signale gesamt** (Master-Akzeptanz ≥20 erfüllt)
- Offene DE-Varianten (Rest des 30er-Postens): M34, M44, M54, M69 (M7/M26/M30 seit Welle 5, M32 seit Welle 6 gedeckt) + NEU-Rest (M6, M17, M29, M39, M40, M50–M52, M58, M68; M56/M72 seit Welle 6, **M63 seit 19.09. gedeckt**)


## Bilanz (#76-Rest M63, 19.09.2026)

- **GEDECKT (neu):** M63 `naturalness_guard.modal_particle_anomaly` — DE-Modalpartikel-Inventar (12 Partikeln, Wortgrenzen-Matching mit Umlaut-Lookarounds), zwei Anomalie-Cues: density (≥ 6 Tokens UND ≥ 2,5 % Wortanteil) + stacking (≥ 2 Sätze mit je ≥ 2 distinkten Partikeln), detect-only, conf 0.45, Quote-Stripping + `genre=dialogue/fiction/spoken`-Suppression. Stub damit ersetzt (#81-Delegation eingelöst). Beleg: Duden-Grammatik-Referenz (REFERENCES.md #40) + own:corpus de-ev-29. Tests: `ModalParticleAnomalyDoD` 3 pos / 3 neg / 2 boundary + detect-only-Verkabelung, 18/18 grün.


## Bilanz (#77-Rest Welle 6, 15.09.2026)

- **GEDECKT (neu, Welle 6):** 3 weitere Muster — M32 `de_rhetorical_setup`, M56 `de_aphorism`, M72 `de_therapeutic_validation` (je 6 Phrasen, conf 0.6, **Voll-Zweibeleg** je Phrase: Wikipedia-Projektseite + own:corpus de-ev-26..28)
- **DE-Signal-Zähler:** 31 + 3 = **34 DE-Signale gesamt**
- Fixtures je Kategorie 3/3/2 in tests/test_de_variant_rest4.py; DE_LAYER-Pin auf 28 Kategorien erweitert (C4: 135/168 Phrasen mit ≥ 2 Belegen — neue 18 Phrasen vollständig zweibelegt)
- Kollisionsdisziplin: „die eigentliche frage ist" bereits in de_authority_floskel → M32-Kategorie mit disjunktem Phrasensatz implementiert (W5-Präzedenzfall #46-Disziplin)

## Bilanz (#77-Rest Welle 4, 13.09.2026)

- **GEDECKT (neu, Welle 4):** 3 weitere Muster — M35 `de_fake_dialog`, M59 `de_faux_candid`, M70 `de_false_agency` (je 6 Phrasen, conf 0.6, **Voll-Zweibeleg** je Phrase: Wikipedia-Projektseite + own:corpus de-ev-20..22)
- **DE-Signal-Zähler:** 28 + 3 = **31 DE-Signale gesamt**
- Fixtures je Kategorie 3/3/2 in tests/test_de_variant_rest2.py; DE_LAYER-Pin auf 22 Kategorien erweitert (C4: 99/132 Phrasen mit ≥ 2 Belegen — neue 18 Phrasen vollständig zweibelegt)
- Kollisionsfix gegenüber Erstentwurf: "die forschung deutet darauf hin" → "die studienlage deutet darauf hin" (Teilstring-Kollision mit de_authority_floskel #46-Disziplin)

## Bilanz (#77-Rest-Batch, 13.09.2026)

- **GEDECKT (neu, #77-Rest):** 3 weitere Muster — M18 `de_chatbot_leftover`, M33 `de_signposting`, M65 `de_copula_avoidance` (je 6 Phrasen, conf 0.6, **Voll-Zweibeleg** je Phrase: Wikipedia-Projektseite + own:corpus de-ev-17..19)
- **DE-Signal-Zähler:** 22 + 3 = **25 DE-Signale gesamt**
- Fixtures je Kategorie 3/3/2 in tests/test_de_variant_rest.py; DE_LAYER-Pin auf 19 Kategorien erweitert (C4: 81/114 Phrasen mit ≥ 2 Belegen — neue 18 Phrasen vollständig zweibelegt)

## Bilanz (Teil 1)

- **GEDECKT (bestehend):** 20 Muster (M9, M13–M16, M19–M25 (Teil), M43, M55, M57)
- **GEDECKT (neu, dieser Batch):** 4 Muster (M46, M47, M48, M49) — `de_typography.py`, detect-only, DE-Sprachgate, je 3/3/2 Fixtures (tests/test_de_typography.py)
- **DE-VARIANTE (→ #77-Layer):** 30 Muster — Phrase-Datenbank-Ausbau (de_calque, de_ai_vocab, de_authority_floskel, de_meta_comment als erste vier Kategorien)
- **NEU:** 18 Muster — davon sprachagnostisch priorisiert: M60 (Synonym-Rotation), M61 (Isometrie); Rest als Kandidaten-Register für Folge-Batches
- **OFFEN (Stub):** M63 Modalpartikel-Anomalie — bewusst Stub bis DE-Inventar steht (#81-Entscheidung)

Kein Muster wird als „automatisch fixbar" behandelt — alle DE-Signale sind detect-only/advisory (Anti-Auto-Rewrite-Disziplin, vgl. SIGNAL-DOD.md).

## Struktur-Signale für Satzanfangs-Ankündigungen und Konnektor-Absätze (#230, detect-only)

- **OpenerAnnouncement** (`rhythm_openers.py`): Frame-basierte Zweiwort-Frames („Ich möchte …", „Ich denke[, …]", „Spannender Punkt.", „Ein weiterer Aspekt ist …", „Die spannende Frage ist …"; EN-Analoga) via Clause-Initial-Anker (#88-Mechanik) statt wachsender Wortliste. **keep_when:** echte Haltungsdifferenzierung — „Ich denke, dass X" mit folgender Begründung (und EN „I think that …") ist ausdrücklich exempt.
- **ParagraphConnectorRate** (`rhythm_openers.py`, advisory): Anteil der Absätze mit additivem Konnektor-Eröffner (Darüber hinaus/Zudem/Ein weiterer (Aspekt|Punkt)/Gleichzeitig/Abschließend/Zusammenfassend + EN-Analoga). Feuert erst ab ≥ 3 Konnektor-Absätzen UND Rate > 0,4. **keep_when:** juristisches/akademisches Genre-Profil (konnektorgeführte Absätze als Hausstil; einzelnes „Darüber hinaus" feuert nie).
- Kein Score-Einfluss (ADR-0006; Test in tests/test_rhythm_openers.py analog test_code_slop).

## Evidence-Verdichtung (RI-2-FU, #76-Rest)

- **Ziel erreicht:** 63/96 de_*-Phrasen (65,6 %) tragen jetzt **≥ 2 unabhängige Belege** (Pin ≥ 50 %, C4 in scripts/check_ssot.py, Manipulationsprobe in tests/test_de_evidence_densification.py). Zweite Belege: eigene handgeschriebene Belegtexte (`eval/de_evidence_texts.jsonl`, source `own:corpus`, je Kategorie ein Text mit 3–4 wörtlich enthaltenen Phrasen) — eigene Handschrift, keine Kopien aus CC BY-SA-Drittkatalogen (Lizenzregel).
- **Dokumentierte Abweichung (33 Phrasen, 34,4 %):** Einzelbeleg (Wikipedia-Projektseite oder own:de-observation/en-pendant). Die Rest-Belegung läuft künftig über den C4-Coverage-Pin — Unterschreiten von 50 % failt das SSOT-Gate.
- **Strukturmetrik-Rest:** M66 (fake_analysis_appendix) und M71 (pseudo_nuance) als detect-only Signale in structure_metrics.py (Konfidenz 0.5, je 3/3/2-Fixtures in tests/test_structure_rest.py). M67 (Ankündigungs-Spaltsatz) bereits als de_announcement_cleft gedeckt — bewusst keine Duplikation (#46).

## Kommentar-Genre-Profil + Engagement-Sequenz (#231, detect-only)

- **Genre-Profil `comment`** (`genre_profiles.py`): Opt-in via `--genre comment` (ADR-0004, kein Auto-Detect). Exempt: Höflichkeitsformeln („Great post", „Thanks for sharing", „Congrats", „Well said" …), zero_weights: burstiness/verbosity (Kurztext-Konvention), decision_threshold 0.30.
- **EngagementCommentDefault** (`engagement_sequences.py`, detect-only): Lob → Paraphrase → Ergänzung → Frage als Default-Engagement-Sequenz. Feuert nur bei vollständiger Vier-Stufen-Sequenz in ≤120 Wörtern; kurze authentische Kommentare feuern nie. Kein Score-Einfluss (ADR-0006-Politik, analog #230); Scoring-Integration zurückgestellt bis Korpuswachstum (ADR-0005).
- **Evals:** 10 handgeschriebene Kommentar-Texte in `eval/control_set.jsonl` (5 Slop-Sequenzen als known_fn mit Sequenz-Nachweis, 5 legitime Hard Negatives, FP-Rate 0 am Genre-Threshold 0.30). Tests: `tests/test_engagement_sequences.py` (7 Tests).

## 2026-09-17: OpenerAnnouncement + ParagraphConnectorRate (#230 / P3)

- **OpenerAnnouncement** (rhetorical_patterns.py, detect-only, Konfidenz 0.45):
  Lob-/Ankuendigungs-Frames am Satzanfang ("Spannender Punkt.", "Ein weiterer Aspekt ist ...",
  "Die spannende Frage ist ...", "Du sprichst einen wichtigen Punkt an") sowie
  text-initiale Ich-Anlaeufe ("Ich moechte/denke/finde/glaube ...") OHNE
  Begruendungsmarker im Satz. Frame-basiert (Platzhalter-Mechanik #83/#88), keine
  wachsende Wortliste. keep_when: echte Haltungsdifferenzierung ("Ich denke, dass X,
  weil Y belegt"), Ritual-Formeln, Verhandlungs-Ankuendigungen.
- **ParagraphConnectorRate** (rhythm_openers.py, advisory, nie gescored): Anteil der
  Absaetze mit additivem Konnektor-Eroeffner (dt./engl.); Signal ab > 50 % und >= 2
  Absaetzen. keep_when: strukturierte Genres (juristisch, regulatorisch, akademisch),
  wo Konnektor-Absaetze Konvention sind.
- Hard Negatives getestet in tests/test_opener_announcement.py (Begruendung im Satz,
  mid-text-Ich, juristischer Einzel-Konnektor, Kurztext).

## 2026-09-17: Genre-Profil comment/message + LinkedIn-Kommentar-Evals (#231 / P4)

- **Genre-Profile `comment` und `message`** (genre_profiles.py, Opt-in via `--genre`,
  ADR-0004: kein Auto-Detect): kurze Saetze und Ritual-Formeln (Grussformeln) sind
  Genres-Konvention, kein Slop — exempt_terms fuer Grussformeln, zero_weights fuer
  verbosity/list_heavy, decision_threshold 0.50. Lob-Auftakt und Triaden bleiben
  voll verdächtig (Advisories verweisen auf OpenerAnnouncement /
  engagement_comment_default / ForcedTriad).
- **`engagement_comment_default`** (rhetorical_patterns.py, detect-only,
  Konfidenz 0.45): feuert erst, wenn EIN Text mindestens 3 der 4 Sequenzelemente
  IN REIHENFOLGE enthaelt (Lob-Anfang -> Paraphrase-Marker -> Ergaenzungs-Ankuendigung
  -> schliessende Frage). Einzelne Elemente (auch Paraphrase + Frage) feuern nicht.
  keep_when: echte FAQ-Konversation/Interview/Moderation.
- **Control-Set-Erweiterung** (eval/control_set.jsonl, 10 -> 20 Texte, ADR-0005
  eigene Handschrift): 5 CommentSlop-Sequenzen (als known_fn dokumentiert — kurze
  Kommentare erreichen die Score-Eskalation nicht; Detektion laeuft detect-only,
  ADR-0006) und 5 legitime LinkedIn-Kommentare als Hard Negatives
  (differenzierter Widerspruch, echte Detailfrage, inhaltliche Zustimmung mit
  Ergaenzung, Kritik am Vergleich, technische Gegenanalyse).
  **FP-Rate auf den 5 legitimen Kommentaren: 0** (kein Signal, Score < 0.08).
- Tests: tests/test_comment_genre.py (TP >= 1, Hard Negatives >= 2 inkl.
  Control-Set-Texte, Opt-in ohne Auto-Detect).
